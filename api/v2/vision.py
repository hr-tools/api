from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
import random
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import sanic
from sanic import response as r
from sanic.exceptions import InvalidUsage, NotFound
from sanic_ext import validate

from .utils import name_color, white_pattern_reserves
import horsereality
import predictor

if TYPE_CHECKING:
    import asyncpg


api = sanic.Blueprint('Vision-v2')
log = logging.getLogger('realtools')


@dataclass
class PartialHorseInfo:
    lifenumber: int
    name: str
    sex: str
    breed: str
    age: Optional[str] = None
    birthdate: Optional[str] = None
    height: Optional[str] = None
    location: Optional[str] = None
    owner: Optional[str] = None
    registry: Optional[str] = None
    predicates: Optional[str] = None


@dataclass
class PredictPayload:
    horse_info: PartialHorseInfo
    layer_urls: Union[List[str], str]  # Shortcut stringified variables
    genes: Optional[dict] = None
    # typing.Dict is not properly recognized so we can't notate this parameter
    # with as much detail as would be desirable


@dataclass
class PredictLifenumberPayload:
    lifenumber: int
    genes: Optional[dict] = None


@api.post('/predict')
@validate(json=PredictPayload)
async def predict(request: sanic.Request, body: PredictPayload):
    """Predict Foal

    Return a prediction of what the foal will look like when it is an adult, including white layers and color info.

    openapi:
    ---
    parameters:
        - name: horse_info
          in: body
          description: Partial info about the horse - `sex` and `breed` are important here
          required: true
          schema:
            type: object
            example: {"lifenumber": 9999999, "name": "Foal Doe 9999999", "sex": "Stallion", "breed": "Akhal-Teke"}
        - name: layer_urls
          in: body
          description: The URLs of the foal's layers
          required: true
          schema:
            type: array
            example: ["https://www.horsereality.com/upload/colours/foals/body/large/d09169762.png", "https://www.horsereality.com/upload/whites/foals/body/large/8984dc670.png", "https://www.horsereality.com/upload/colours/foals/mane/large/d09169762.png", "https://www.horsereality.com/upload/colours/foals/tail/large/4094b3ca8.png"]
        - name: genes
          in: body
          description: Gene information to use for color info overrides and white layer supplementation
          required: false
          schema:
            type: object
            example: {"agouti": "A/a", "roan": "RN"}
    responses:
        '200':
            description: Some prediction information.
        '400':
            description: Bad request.
        '404':
            description: Something was not found. Usually because of missing data for the foal's breed or its layers.
    """

    # 2022-08-09: Our standard authentication system does not work anymore,
    # so we have to rely on clients to grab the layers for us.

    # 2022-09-15: The horsereality package has been updated to support another
    # form of direct authentication, and as such Vision has been split into
    # this route as well as one that accepts a lifenumber.

    payload: Dict[str, Any] = asdict(body)

    horse_info: PartialHorseInfo = payload['horse_info']
    layer_urls: List[str] = payload['layer_urls']
    genes: Dict[str, str] = payload['genes'] or {}

    if isinstance(layer_urls, str):
        try:
            layer_urls = layer_urls.splitlines()
        except:
            raise InvalidUsage('Invalid stringified layer URLs passed.', extra={'name': 'layers_invalid_string'})

    if not layer_urls or not isinstance(layer_urls, list):
        raise InvalidUsage('Invalid layer URLs passed.', extra={'name': 'layers_invalid_type'})

    hr: horsereality.Client = request.app.ctx.hr
    try:
        layers = []
        for layer_url in layer_urls:
            if not layer_url.startswith('https://'):
                # We accept bare keys like colours/foals/tail/large/id as well as full URLs
                # This is obviously not bulletproof but clients will just get
                # a validation error if they don't provide an expected format
                layer_url = f'https://www.horsereality.com/upload/{layer_url}.png'
            layer = hr.create_layer(layer_url)
            layers.append(layer)
    except ValueError:
        raise InvalidUsage('Invalid layer URL(s).', extra={'name': 'layers_invalid'})

    horse_types = set(layer.horse_type for layer in layers)
    if len(horse_types) != 1:
        raise InvalidUsage('Mismatched layer URLs provided.', extra={'name': 'layers_unmatching'})
    if list(horse_types)[0] != 'foals':
        raise InvalidUsage('This horse is not a foal.', extra={'name': 'layers_not_foal'})

    horse_info['layers'] = {'foal': layers}
    horse = horsereality.Horse(http=hr.http, data=horse_info)

    return await predict_with_layers(request, horse, genes)


@api.post('/predict-lifenumber')
@validate(json=PredictLifenumberPayload)
async def predict(request: sanic.Request, body: PredictLifenumberPayload):
    """Predict Foal with Lifenumber

    Return a prediction of what the foal will look like when it is an adult, including white layers and color info.
    This endpoint differs from Predict Foal in that it does not require layer URLs at the expense of a slightly slower result time.

    openapi:
    ---
    parameters:
        - name: lifenumber
          in: body
          description: The foal's lifenumber
          required: true
          schema:
            type: integer
        - name: genes
          in: body
          description: Gene information to use for color info overrides and white layer supplementation
          required: false
          schema:
            type: object
            example: {"agouti": "A/a", "roan": "RN"}
    responses:
        '200':
            description: Some prediction information.
        '400':
            description: Bad request.
        '404':
            description: Something was not found. Usually because of missing data for the foal's breed or its layers.
    """

    payload: Dict[str, Any] = asdict(body)

    lifenumber: int = payload['lifenumber']
    genes: Dict[str, str] = payload['genes'] or {}

    hr: horsereality.Client = request.app.ctx.hr
    horse = await hr.get_horse(lifenumber)

    if not horse.foal_layers:
        raise InvalidUsage('This horse is not a foal.', extra={'name': 'layers_not_foal'})

    if not horse.is_foal() and horse.foal_lifenumber:
        # SITE-17
        # We are looking at the dam, which means we do not know the foal's sex.
        # Doing this also allows us to show the foal's name and always link to the foal's page, but this is less important.
        horse = await horse.fetch_foal()

    return await predict_with_layers(request, horse, genes)


async def predict_with_layers(request: sanic.Request, horse: horsereality.Horse, genes: Dict[str, str]):
    pool: asyncpg.Pool = request.app.ctx.psql_pool
    breed: str = horse.breed
    sex: str = horse.sex.lower()
    if sex == 'gelding':
        sex = 'stallion'

    # Map out the foal's layer IDs
    foal_colour_ids = []
    foal_white_ids = []
    for layer in horse.layers:
        if layer.type is horsereality.LayerType.colours:
            foal_colour_ids.append(layer.id)
        elif layer.type is horsereality.LayerType.whites:
            foal_white_ids.append(layer.id)

    # Get layer orders
    orders = getattr(horsereality.BreedOrders, breed, None)
    if not orders or (orders and not orders.value.get(sex)):
        log.debug(f'Found no orders for breed {breed!r} while predicting {horse.lifenumber}')
        raise NotFound('No data is available for this breed or sex, sorry. This will usually only happen on newer breeds that Realvision does not support yet.', extra={'name': 'no_data_orders'})
    orders = orders.value[sex]

    # Match to adult layers
    colour_layer_rows = await pool.fetch(
        '''
        SELECT dilution, body_part, stallion_id, mare_id, foal_id, base_genes, color
        FROM color_layers
        WHERE breed = $1
        AND foal_id = ANY($2::text[])
        ''',
        breed, foal_colour_ids
    )
    if not colour_layer_rows:
        log.debug(f'Found no colour layers while predicting {horse.lifenumber} - IDs {json.dumps(foal_colour_ids)}')
        raise NotFound('No data is available for this horse, sorry.', extra={'name': 'no_data_horse'})

    # Duplicate tracking
    colour_layer_id_counts = [row['foal_id'] for row in colour_layer_rows]

    untestable_white_layer_rows = await pool.fetch(
        '''
        SELECT body_part, stallion_id, mare_id, rab, roan
        FROM white_layers
        WHERE breed = $1
        AND foal_id = ANY($2::text[])
        ''',
        breed, foal_white_ids
    )

    testable_white_layer_rows = await pool.fetch(
        '''
        SELECT body_part, stallion_id, mare_id, rab, roan
        FROM testable_white_layers
        WHERE breed = $1
        AND foal_id = ANY($2::text[])
        ''',
        breed, foal_white_ids
    )

    white_layer_rows = untestable_white_layer_rows + testable_white_layer_rows

    roan_rab_rows = await pool.fetch(
        '''
        SELECT body_part, stallion_id, mare_id, color
        FROM testable_white_layers
        WHERE breed = $1
        AND color IN ('Roan', 'Rabicano')
        ''',
        breed
    )
    roans = {row['body_part']: row for row in roan_rab_rows if row['color'] == 'Roan'}
    rabs = {row['body_part']: row for row in roan_rab_rows if row['color'] == 'Rabicano'}

    color_info = await name_color(request.app, breed, horse.layers)

    white_urls = {}
    is_roan = False
    is_rab = False
    white_pattern_color_name = ''
    white_pattern_genotype_names = set()
    for row in white_layer_rows:
        adult_id = row[f'{sex}_id']
        if adult_id:
            white_urls[row['body_part']] = []
            if row['rab'] is True:
                is_rab = True
                white_id = rabs.get(row['body_part'], {}).get(f'{sex}_id')
                if white_id:
                    url = f'https://www.horsereality.com/upload/whites/{sex}s/{row["body_part"]}/large/{white_id}.png'
                    white_urls[row['body_part']].append(url)

            if row['roan'] is True:
                is_roan = True
                white_id = roans.get(row['body_part'], {}).get(f'{sex}_id')
                if white_id:
                    url = f'https://www.horsereality.com/upload/whites/{sex}s/{row["body_part"]}/large/{white_id}.png'
                    white_urls[row['body_part']].append(url)

            url = f'https://www.horsereality.com/upload/whites/{sex}s/{row["body_part"]}/large/{adult_id}.png'
            white_urls[row['body_part']].append(url)

            # brabant foals don't have white layers on their tail and mane but adults do
            if is_roan and breed == 'brabant_horse':
                white_id = roans['tail'][f'{sex}_id']
                url = f'https://www.horsereality.com/upload/whites/{sex}s/tail/large/{white_id}.png'
                white_urls['tail'] = [url]

                white_id = roans['mane'][f'{sex}_id']
                url = f'https://www.horsereality.com/upload/whites/{sex}s/mane/large/{white_id}.png'
                white_urls['mane'] = [url]
                # the brabant's order of body,tail,mane is very convenient for us here

            if is_rab:
                white_id = rabs['tail'][f'{sex}_id']
                url = f'https://www.horsereality.com/upload/whites/{sex}s/tail/large/{white_id}.png'
                white_urls['tail'] = [url]

    if white_layer_rows:
        # name_color can include a potentially misleading note when only untestable white layers exist
        notes = color_info.get('notes', [])
        try:
            notes.remove('white_layer_unmatched')
        except ValueError:
            pass

    urls_data = {}
    for row in colour_layer_rows:
        adult_id = row[f'{sex}_id']
        if adult_id:
            url = f'https://www.horsereality.com/upload/colours/{sex}s/{row["body_part"]}/large/{adult_id}.png'
            urls_data[row['body_part']] = {
                'colours': url,
                'colours_id': adult_id,
                'foal_colours_id': row['foal_id'],
                'whites': white_urls.get(row['body_part']),
                'white_reserves': []
            }

    if not urls_data or 'body' not in urls_data:
        # TODO: Autotrack here
        raise NotFound('Some or all of this foal\'s layers are not able to be predicted right now.')

    # Base name overrides
    genes_extension = genes.get('extension')
    genes_agouti = genes.get('agouti')

    body_foal_id = urls_data['body']['foal_colours_id']
    if colour_layer_id_counts.count(body_foal_id) >= 2:
        possible_duplicates = {foal_id: {} for foal_id in colour_layer_id_counts}
        for row in colour_layer_rows:
            possible_duplicates[row['foal_id']][row['base_genes']] = dict(row)

        def overwrite_info_display(base_genes):
            try:
                row = possible_duplicates[body_foal_id][base_genes]
            except KeyError:
                pass
            else:
                color_info['dilution'] = (row['base_genes'] + ' ' + (row['dilution'] if row['dilution'].lower() != 'no dilution' else '')) or None
                color_info['color'] = row['color']

        # handle duplicates by checking base colour options
        if genes_extension == 'e/e':
            # chestnut
            overwrite_info_display('ee')
            overwrite_info_display('ee G')

        elif genes_extension == 'E/e' and (genes_agouti == 'a/a' or genes_agouti is None):
            # black
            overwrite_info_display('E aa')
            overwrite_info_display('E aa G')

        elif genes_extension == 'E/e' and genes_agouti == 'A/a':
            # bay
            overwrite_info_display('E A')
            overwrite_info_display('E A G')

    # White pattern reserves
    if white_pattern_reserves.get(breed):
        gene_names = [
            # testable
            'frame', 'splash_white', 'tobiano', 'roan',
            # untestable
            'rabicano', 'sabino2'
        ]
        gene_name_overrides = {
            'SW1/SW1': 'Double Splash',
            'TO/TO': 'Homozygous Tobiano'
        }
        gene_values = {}
        for gene_name in gene_names:
            if genes.get(gene_name):
                value = genes.get(gene_name)
                name = gene_name.replace('_', ' ').title()
                if value in gene_name_overrides:
                    name = gene_name_overrides[value]
                gene_values[value] = name
                # how the turns have tabled

        # when a horse has both, the artwork is different instead of just having two layered images
        if gene_values.get('TO') and gene_values.get('OLW'):
            gene_values.pop('TO')
            gene_values.pop('OLW')
            gene_values['OLW TO'] = 'Tovero'

        if gene_values.get('SW1/SW1') and gene_values.get('OLW'):
            gene_values.pop('SW1/SW1')
            gene_values.pop('OLW')
            gene_values['OLW SW1/SW1'] = 'Frame Double Splash'

        if gene_values.get('SW1') and gene_values.get('OLW'):
            gene_values.pop('SW1')
            gene_values.pop('OLW')
            gene_values['OLW SW1'] = 'Frame Splash'

        if gene_values.get('SW1') and gene_values.get('TO'):
            gene_values.pop('SW1')
            gene_values.pop('TO')
            gene_values['SW1 TO'] = 'Splash Tobiano'

        if gene_values.get('SW1') and gene_values.get('TO/TO'):
            gene_values.pop('SW1')
            gene_values.pop('TO/TO')
            gene_values['SW1 TO/TO'] = 'Splash Homozygous Tobiano'

        if gene_values.get('SW1') and gene_values.get('rb/rb'):
            gene_values.pop('SW1')
            gene_values.pop('rb/rb')
            gene_values['SW1 rb/rb'] = 'Splash Rabicano'

        if gene_values.get('SW1') and gene_values.get('sb/sb'):
            gene_values.pop('SW1')
            gene_values.pop('sb/sb')
            gene_values['SW1 sb/sb'] = 'Splash Sabino2'

        if gene_values.get('SW1/SW1') and gene_values.get('TO'):
            gene_values.pop('SW1/SW1')
            gene_values.pop('TO')
            gene_values['SW1/SW1 TO'] = 'Double Splash Tobiano'

        if gene_values.get('SW1/SW1') and gene_values.get('TO/TO'):
            gene_values.pop('SW1/SW1')
            gene_values.pop('TO/TO')
            gene_values['SW1/SW1 TO/TO'] = 'Double Splash Homozygous Tobiano'

        if gene_values.get('SW1/SW1') and gene_values.get('sb/sb'):
            gene_values.pop('SW1/SW1')
            gene_values.pop('sb/sb')
            gene_values['SW1/SW1 sb/sb'] = 'Double Splash Sabino2'

        white_pattern_color_name_to_add = set()
        for gene_value, gene_name in gene_values.items():
            try:
                replace_with = white_pattern_reserves[breed][gene_value][sex]
            except KeyError:
                # no reserves available
                continue
            else:
                if (
                    urls_data.get('body', {}).get('whites')
                    or urls_data.get('mane', {}).get('whites')
                    or urls_data.get('tail', {}).get('whites')
                ):
                    # ignore if whites were already found anywhere on the horse (#2)
                    continue
                for body_part, white_id in replace_with.items():
                    if not white_id:
                        # no value for this body part
                        continue

                    url = f'https://www.horsereality.com/upload/whites/{sex}s/{body_part}/large/{white_id}.png'
                    urls_data[body_part] = urls_data.get(body_part, {'colours': None, 'white_reserves': []})
                    urls_data[body_part]['white_reserves'].append(url)

                    # color & genotype display
                    # explicitly declare these two to make sure they get listed at
                    # the end of the display
                    if gene_name == 'Roan':
                        is_roan = True
                    elif gene_name == 'Rabicano':
                        is_rab = True
                    else:
                        white_pattern_color_name_to_add.add(gene_name)
                        white_pattern_genotype_names.add(gene_value)

        white_pattern_color_name += ' ' + ' '.join(white_pattern_color_name_to_add)

    # Checking for gaps in data and attempting to fill them in with similar layers
    before_table = {
        # This has a static order because we are mimicking how layers are stored in the database
        'body': 'tail',
        'mane': 'body',
        'tail': 'mane',
    }

    # colours
    for missing in ['mane', 'tail']:
        # It _could be_ missing
        if missing not in urls_data:
            # It's missing
            possible_layer_rows = await pool.fetch(
                '''
                SELECT dilution, body_part, stallion_id, mare_id, base_genes, color
                FROM color_layers
                WHERE breed = $1
                AND color = $2
                ''',
                breed, color_info['color']
            )
            before = before_table[missing]
            try:
                before_id = urls_data[before]['colours_id']
            except KeyError:
                # That one is missing too, abort
                break

            # I think this is not actually useful to have
            missing_is_after = list(before_table.keys()).index(missing) > list(before_table.keys()).index(before)

            for index, row in enumerate(possible_layer_rows):
                if row[f'{sex}_id'] == before_id and row['body_part'] == before:
                    missing_row = possible_layer_rows[index + (1 if missing_is_after else -1)]
                    adult_id = missing_row[f'{sex}_id']
                    url = f'https://www.horsereality.com/upload/colours/{sex}s/{missing}/large/{adult_id}.png'
                    urls_data[missing] = {
                        'colours': url,
                    }
                    break

    # whites
    if any(missing not in white_urls for missing in ('mane', 'tail')):
        # One of them is missing
        possible_layer_rows = await pool.fetch(
            '''
            SELECT body_part, stallion_id, mare_id, color
            FROM testable_white_layers
            WHERE breed = $1
            AND color = $2
            ''',
            breed, color_info['_raw_testable_color']
        )
        try:
            possible_before_urls = white_urls['body']
        except KeyError:
            # Body is missing, abort
            pass
        else:
            for possible_before_url in possible_before_urls:
                before_id = horsereality.Layer(http=None, url=possible_before_url).id  # This is sort of overkill but it's convenient

                for index, row in enumerate(possible_layer_rows):
                    if row[f'{sex}_id'] == before_id and row['body_part'] == 'body':
                        if 'mane' not in white_urls:
                            missing_is_after = list(before_table.keys()).index('mane') > list(before_table.keys()).index('body')
                            missing_row = possible_layer_rows[index + (1 if missing_is_after else -1)]
                            adult_id = missing_row[f'{sex}_id']
                            if adult_id:
                                url = f'https://www.horsereality.com/upload/whites/{sex}s/mane/large/{adult_id}.png'
                                urls_data['mane'] = urls_data.get('mane', {'colours': None})
                                urls_data['mane']['whites'] = [url]

                        if 'tail' not in white_urls:
                            missing_is_after = list(before_table.keys()).index('tail') > list(before_table.keys()).index('body')
                            missing_row = possible_layer_rows[index + (2 if missing_is_after else -2)]
                            adult_id = missing_row[f'{sex}_id']
                            if adult_id:
                                url = f'https://www.horsereality.com/upload/whites/{sex}s/tail/large/{adult_id}.png'
                                urls_data['tail'] = urls_data.get('tail', {'colours': None})
                                urls_data['tail']['whites'] = [url]

                        break

    # We don't need this anymore
    color_info.pop('_raw_testable_color', None)

    # We use a dict for urls_data instead of just a list to avoid duplicate layers that don't get seen
    urls_raw = [{'body_part': key, **value} for key, value in urls_data.items()]
    urls_raw.sort(key=lambda d: orders.index(d['body_part']))
    complete_layers = []
    for d in urls_raw:
        complete_layers.append(horsereality.Layer(http=None, url=d['colours']))
        if d.get('whites'):
            for white_url in d['whites']:
                layer = horsereality.Layer(http=None, url=white_url)
                complete_layers.append(layer)
        if d.get('white_reserves'):
            for white_url in d['white_reserves']:
                layer = horsereality.Layer(http=None, url=white_url)
                complete_layers.append(layer)

    # White pattern names
    if white_pattern_color_name and white_pattern_color_name != 'Roan':
        color_info['color'] += (' ' + white_pattern_color_name)
    if is_roan and 'Roan' not in color_info['color']:
        color_info['color'] += ' Roan'
    if is_rab and 'Rabicano' not in color_info['color']:
        color_info['color'] += ' Rabicano'

    if white_pattern_genotype_names:
        color_info['dilution'] += (' ' + (' '.join(white_pattern_genotype_names)))
    if is_roan:
        color_info['dilution'] += ' RN'
    if is_rab:
        color_info['dilution'] += ' rb/rb'

    # We include these extra details for the "Import to Multi" button
    # They _could be_ filled in by the client, though
    adult_layer_details = []
    for layer in complete_layers:
        layer_data = layer.to_dict()
        layer_data['enabled'] = True
        layer_data['index'] = complete_layers.index(layer)
        layer_data['key_id'] = f'{random.randint(10000, 99999)}-{layer.id}'
        adult_layer_details.append(layer_data)

    color_info['dilution'] = color_info['dilution'].strip()
    color_info['color'] = color_info['color'].strip()

    horse_data = horse.to_dict()
    # We don't need these
    horse_data.pop('foal_lifenumber')
    horse_data.pop('foal')
    horse_data.pop('layers')

    return r.json(
        {
            'horse': horse_data,
            'color_info': color_info,
            'prediction': {
                'layers': adult_layer_details,
            },
            'selected_genes': genes,  # We use this behind the scenes for share query arguments
        },
        headers=request.app.ctx.cors_headers(request),
    )


async def cors_preflight(request: sanic.Request):
    return r.empty(headers=request.app.ctx.cors_headers(request))


api.add_route(cors_preflight, '/predict', ['OPTIONS'])
api.add_route(cors_preflight, '/predict-lifenumber', ['OPTIONS'])


# This is a legacy endpoint for one of our local tools - it is not useful for
# most people and it is not used in any of our end-user applications.
@api.post('/parse-sheet')
async def parse_sheet(request):
    file = request.files.get('csv')
    if not file:
        raise InvalidUsage('Must provide a CSV to parse.')

    parser = predictor.SheetParser()
    try:
        layers = parser.parse(raw=file.body.decode('utf-8'))
    except Exception as exc:
        log.debug(f'Failed to parse a sheet: {exc.__class__.__name__} {str(exc)}')
        raise InvalidUsage('Invalid CSV data.')

    return r.json(layers, status=200)


@api.options('/parse-sheet')
async def cors_preflight_parse_sheet(request):
    return r.empty(headers={'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Origin': '*'})
