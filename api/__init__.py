import logging
import json

from sanic import Blueprint

from .merge import api as merge_api
from .vision import api as vision_api

api = Blueprint.group(merge_api, vision_api, url_prefix='/api')

log = logging.getLogger('realtools')

@api.middleware('request')
async def log_request(request):
    log.info(f'Received {request.method} {request.path.replace("/api", "", 1)} with {json.dumps(request.json)}')

@api.middleware('response')
async def log_response(request, response):
    log.info(f'Returned {response.status} to {request.method} {request.path.replace("/api", "", 1)}')
