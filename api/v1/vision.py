import base64
import datetime
from io import BytesIO
import logging
import random
import re
import traceback
import json

import sanic
from sanic import response as r

from .utils import dissect_layer_path, white_pattern_reserves
import predictor

api = sanic.Blueprint('Vision-v1')

config = json.load(open('config.json'))
run_address = config.get('address', 'localhost')
run_port = config.get('port', 2965)

log = logging.getLogger('realtools')

#@api.post('/predict')
async def predict(request):
    payload = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    url = payload.get('url')
    if not url or not isinstance(url, str):
        return r.json({'message': 'Invalid request.'}, status=400)

    use_watermark = payload.get('watermark', True)
    if not isinstance(use_watermark, bool):
        return r.json({'message': 'Invalid type for watermark.'}, status=400)

    match = re.match(r'https:\/\/(v2\.|www\.)?horsereality\.(com)\/horses\/(\d{1,10})\/', url)
    if not match:
        return r.json({'message': 'Invalid URL.'}, status=400)

    # fetch layers
    response = await request.app.ctx.session.post(f'http://{run_address}:{run_port}/v1/layers', json={'url': url, 'use_foal': True})
    data = await response.json()
    if response.status >= 400:
        return r.json(data, status=response.status)

    sex = data['details']['sex'].replace('gelding', 'stallion')
    layers = data['layers']
    breed = data['details']['breed'].lower().replace('-', '_').replace(' ', '_')
    foal_ids = [d['id'] for d in layers]
    foal_colour_ids = [d['id'] for d in layers if d['type'] == 'colours']
    foal_white_ids = [d['id'] for d in layers if d['type'] == 'whites']

    # base override and white pattern reserves
    genes = payload.get('genes') or {}
    # base color
    genes_extension = genes.get('extension')
    genes_agouti = genes.get('agouti')

    if layers[0]['horse_type'] != 'foals':
        return r.json({'message': 'This horse is not a foal.'}, status=400)

    # get layer orders
    orders = predictor.SheetParser.orders.get(breed)
    if not orders or (orders and not orders.get(sex)):
        log.debug(f'Found no orders for breed {breed!r} while predicting {url}')
        return r.json({'message': 'No data is available for this breed, sorry.'}, status=404)

    orders = orders[sex]

    # match to adult layers
    colour_layer_rows = await request.app.ctx.psql_pool.fetch(
        '''
        SELECT dilution, body_part, stallion_id, mare_id, foal_id, base_genes, color
        FROM color_layers
        WHERE breed = $1
        AND foal_id = ANY($2::text[])
        ''',
        breed, foal_colour_ids
    )
    if not colour_layer_rows:
        log.debug(f'Found no colour layers while predicting {url} - IDs {json.dumps(foal_colour_ids)}')
        return r.json({'message': 'No data is available for this horse, sorry.'}, status=404)

    # duplicate tracking
    colour_layer_id_counts = [row['foal_id'] for row in colour_layer_rows]

    untestable_white_layer_rows = await request.app.ctx.psql_pool.fetch(
        '''
        SELECT body_part, stallion_id, mare_id, roan, rab, roan_rab
        FROM white_layers
        WHERE breed = $1
        AND foal_id = ANY($2::text[])
        ''',
        breed, foal_white_ids
    )

    testable_white_layer_rows = await request.app.ctx.psql_pool.fetch(
        '''
        SELECT body_part, stallion_id, mare_id, white_gene, color, roan, rab, roan_rab
        FROM testable_white_layers
        WHERE breed = $1
        AND foal_id = ANY($2::text[])
        ''',
        breed, foal_white_ids
    )

    white_layer_rows = untestable_white_layer_rows + testable_white_layer_rows
    roan_rab_rows = await request.app.ctx.psql_pool.fetch(
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

    white_urls = {}
    is_roan = False
    is_rab = False
    white_pattern_color_name = ''
    white_pattern_genotype_names = set()
    for row in white_layer_rows:
        testable = False
        if row in testable_white_layer_rows:
            testable = True

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

            # append to the color name
            if testable:
                white_pattern_color_name = row['color']
                if row['white_gene']:
                    white_pattern_genotype_names.add(row['white_gene'])

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
            base_genes = row['base_genes']
            data['details']['dilution'] = (base_genes + ' ' + (row['dilution'] if row['dilution'].lower() != 'no dilution' else '')) or None
            data['details']['color'] = row['color']

    if not urls_data or 'body' not in urls_data:
        return r.json({'message': 'Some or all of this foal\'s layers are not able to be predicted right now.'}, status=404)

    # base names override
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
                data['details']['dilution'] = (row['base_genes'] + ' ' + (row['dilution'] if row['dilution'].lower() != 'no dilution' else '')) or None
                data['details']['color'] = row['color']

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

    # white pattern reserves
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

        if gene_values.get('SW1') and gene_values.get('rab/rab'):
            gene_values.pop('SW1')
            gene_values.pop('rab/rab')
            gene_values['SW1 rab/rab'] = 'Splash Rabicano'

        if gene_values.get('SW1') and gene_values.get('sab2/sab2'):
            gene_values.pop('SW1')
            gene_values.pop('sab2/sab2')
            gene_values['SW1 sab2/sab2'] = 'Splash Sabino2'

        if gene_values.get('SW1/SW1') and gene_values.get('TO'):
            gene_values.pop('SW1/SW1')
            gene_values.pop('TO')
            gene_values['SW1/SW1 TO'] = 'Double Splash Tobiano'

        if gene_values.get('SW1/SW1') and gene_values.get('TO/TO'):
            gene_values.pop('SW1/SW1')
            gene_values.pop('TO/TO')
            gene_values['SW1/SW1 TO/TO'] = 'Double Splash Homozygous Tobiano'

        if gene_values.get('SW1/SW1') and gene_values.get('sab2/sab2'):
            gene_values.pop('SW1/SW1')
            gene_values.pop('sab2/sab2')
            gene_values['SW1/SW1 sab2/sab2'] = 'Double Splash Sabino2'

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

    if breed == 'suffolk_punch':
        # edge case since suffolk foals don't have tail layers
        possible_layer_rows = await request.app.ctx.psql_pool.fetch(
            '''
            SELECT dilution, body_part, stallion_id, mare_id, base_genes, color
            FROM color_layers
            WHERE breed = $1
            AND color = $2
            ''',
            breed, data['details']['color']
        )
        mane_id = urls_data['mane']['colours_id']
        for index, row in enumerate(possible_layer_rows):
            if row[f'{sex}_id'] == mane_id and row['body_part'] == 'mane':
                tail_row = possible_layer_rows[index+1]
                adult_id = tail_row[f'{sex}_id']
                url = f'https://www.horsereality.com/upload/colours/{sex}s/tail/large/{adult_id}.png'
                urls_data['tail'] = {
                    'colours': url
                }
                break

    # we use a dict for urls_data instead of just a list to avoid duplicate
    # layers that don't get seen and just cause extra processing time
    urls_raw = [{'body_part': key, **value} for key, value in urls_data.items()]
    urls_raw.sort(key=lambda d: orders.index(d['body_part']))
    complete_urls = []
    for d in urls_raw:
        complete_urls.append(d['colours'])
        if d.get('whites'):
            for white_url in d['whites']:
                complete_urls.append(white_url)
        if d.get('white_reserves'):
            for white_url in d['white_reserves']:
                complete_urls.append(white_url)

    # merge
    response = await request.app.ctx.session.post(f'http://{run_address}:{run_port}/v1/merge/multiple', json={'urls': complete_urls, 'watermark': use_watermark})
    merged_data = await response.json()
    if response.status >= 400:
        return r.json(merged_data, status=response.status)

    # white pattern names
    if white_pattern_color_name and white_pattern_color_name != 'Roan':
        data['details']['color'] += (' ' + white_pattern_color_name)
    if is_roan:
        data['details']['color'] += ' Roan'
    if is_rab:
        data['details']['color'] += ' Rabicano'

    if white_pattern_genotype_names:
        data['details']['dilution'] += (' ' + (' '.join(white_pattern_genotype_names)))
    if is_roan:
        data['details']['dilution'] += ' RN'
    if is_rab:
        data['details']['dilution'] += ' rab/rab'

    adult_layer_details = []
    for layer_url in complete_urls:
        dissected = dissect_layer_path(layer_url.replace('https://www.horsereality.com', ''))
        dissected['large_url'] = layer_url
        dissected['small_url'] = layer_url.replace('large', 'small')
        dissected['enabled'] = True
        dissected['index'] = complete_urls.index(layer_url)
        dissected['key_id'] = f'{str(random.randint(10000, 99999))}-{dissected["id"]}'
        adult_layer_details.append(dissected)

    merged_data['id'] = data['id']
    merged_data['tld'] = data['tld']
    merged_data['name'] = re.sub(r' - Horse Reality$', '', data['details']['title'])
    merged_data['details'] = data['details']
    merged_data['layers'] = adult_layer_details  # for "Import to Multi"
    return r.json(merged_data)

@api.options('/parse-sheet')
async def cors_preflight_parse_sheet(request):
    return r.empty(headers={
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*'
    })

@api.post('/parse-sheet')
async def parse_sheet(request):
    file = request.files.get('csv')
    if not file:
        return r.json({'message': 'Must provide a CSV to parse.'}, status=400, headers={'Access-Control-Allow-Origin': '*'})

    parser = predictor.SheetParser()
    try:
        layers = parser.parse(raw=file.body.decode('utf-8'))
    except Exception as exc:
        log.debug(f'Failed to parse a sheet: {exc.__class__.__name__} {str(exc)}')
        return r.json({'message': 'Invalid CSV data.'}, status=400, headers={'Access-Control-Allow-Origin': '*'})

    return r.json(layers, status=200, headers={'Access-Control-Allow-Origin': '*'})
