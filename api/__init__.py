import logging
from sanic import Blueprint
# from .v1 import api as v1
from .v2 import api as v2

api = Blueprint.group(v2)
api_reroute = Blueprint.group(api, version_prefix='/api/v')
api_default = Blueprint.group(*v2.blueprints, url_prefix='/api', version=None)

log = logging.getLogger('realtools')

@api.middleware('request')
async def log_request(request):
    log.info(f'Received {request.method} {request.path} with {request.body.decode("utf-8")}')

@api.middleware('response')
async def log_response(request, response):
    log.info(f'Returned {response.status} to {request.method} {request.path}')
