from __future__ import annotations

from dataclasses import asdict, dataclass
import logging
from typing import List

import sanic
from sanic import response as r
from sanic.exceptions import InvalidUsage, NotFound, ServerError
from sanic_ext import validate

from .utils import name_color
import horsereality


api = sanic.Blueprint('Horses-v2')
log = logging.getLogger('realtools')


@dataclass
class DetermineColorParams:
    breed: str
    layer: List[str]


@api.get('/color')
@validate(query=DetermineColorParams)
async def determine_color_layers(request: sanic.Request, query: DetermineColorParams):
    """Determine Color by Layers

    Get color info for a given breed and list of layer keys.

    openapi:
    ---
    responses:
        '200':
            description: Some color info.
        '400':
            description: Bad request.
        '404':
            description: Something was not found. Usually because of missing data for the horse's breed or its layers.
    """

    payload = asdict(query)
    layer_urls: List[str] = payload['layer']

    if not layer_urls:
        raise InvalidUsage('Invalid layer URLs passed.', extra={'name': 'layers_invalid_type'})

    hr: horsereality.Client = request.app.ctx.hr
    try:
        layers: List[horsereality.Layer] = []
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

    breed: str = payload['breed'].lower().replace(' ', '_').replace('-', '_')

    try:
        color_info = await name_color(request.app, breed, layers)
    except:
        raise ServerError('', extra={'name': 'colors_failed'})

    if color_info is None:
        raise NotFound('', extra={'name': 'colors_no_info_available'})

    color_info.pop('_raw_testable_color', None)
    return r.json(color_info, headers=request.app.ctx.cors_headers(request))


@dataclass
class GetHorseQuery:
    use_foal: str = None
    return_layers: str = 'true'
    return_color_info: str = 'false'


@api.get('/horses/<lifenumber:int>')
@validate(query=GetHorseQuery)
async def get_horse(request: sanic.Request, query: GetHorseQuery, lifenumber: int):
    if lifenumber < 1:
        return InvalidUsage('Invalid lifenumber.')

    params = asdict(query)
    use_foal = params['use_foal'] == 'true' if params['use_foal'] is not None else None
    return_layers = params['return_layers'] == 'true'
    return_color_info = params['return_color_info'] == 'true'

    hr: horsereality.Client = request.app.ctx.hr
    horse = await hr.get_horse(lifenumber)
    if not horse.is_foal() and horse.foal_lifenumber and use_foal is True:
        horse = await horse.fetch_foal()

    data = {
        'horse': horse.to_dict(),
    }

    if return_color_info:
        try:
            color_info = await name_color(request.app, horse.breed, horse.layers)
        except:
            raise ServerError('', extra={'name': 'colors_failed'})
        else:
            color_info.pop('_raw_testable_color', None)
            data['color_info'] = color_info

    if return_layers is False:
        data['horse'].pop('layers')

    return r.json(data, headers=request.app.ctx.cors_headers(request))


async def cors_preflight(request: sanic.Request):
    return r.empty(headers=request.app.ctx.cors_headers(request))


api.add_route(cors_preflight, '/horses/<lifenumber>', ['OPTIONS'])
#api.add_route(cors_preflight, '/horses/<lifenumber>/color', ['OPTIONS'])
api.add_route(cors_preflight, '/color', ['OPTIONS'])
