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


api = sanic.Blueprint('Color-v2')
log = logging.getLogger('realtools')


@api.options('/color')
async def cors_preflight_predict(request: sanic.Request):
    return r.empty(headers=request.app.ctx.cors_headers(request))


@dataclass
class DetermineColorParams:
    breed: str
    layer: List[str]


@api.get('/color')
@validate(query=DetermineColorParams)
async def determine_color(request: sanic.Request, query: DetermineColorParams):
    """Determine Color

    Get color info for a given set of breed, sex, and layer keys.

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

    # 2022-08-09: Our standard authentication system does not work anymore,
    # so we have to rely on clients to grab the layers for us

    payload = asdict(query)
    layer_urls: List[str] = payload['layer']

    if not layer_urls:
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
            layer = horsereality.Layer(http=hr.http, url=layer_url)
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
    return r.json(
        color_info,
        headers=request.app.ctx.cors_headers(request),
    )
