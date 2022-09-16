import json
import traceback
from urllib.parse import urlparse

import aiohttp
import asyncpg
import logging
from redis import asyncio as aioredis

import sanic
from sanic import response as r
from sanic.exceptions import SanicException

from api import api, api_reroute, api_default

import horsereality

config = json.load(open('config.json'))
debug: bool = config.get('debug', False)

logger = logging.getLogger('realtools')
logger.addHandler(logging.NullHandler())

if config.get('log') is not None:
    logger.setLevel(getattr(logging, config.get('log_level', 'INFO')))
    handler = logging.FileHandler(filename=config['log'], encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

app = sanic.Sanic('Realtools')
app.blueprint(api)  # main API blueprint - routes available on the top level
app.blueprint(api_reroute)  # directs `/api/...` calls to the top level
app.blueprint(api_default)  # defaults calls with no specifier to a version
app.config.FALLBACK_ERROR_FORMAT = 'json'
app.ctx.__realtools_version__ = 'v2.2'
app.ctx.realtools_config = config
app.ctx.debug = debug

def origin_allowed_cors(origin: str) -> bool:
    """Returns whether a given origin is allowed under Realtools's CORS policy."""
    try:
        parsed = urlparse(origin)
    except:
        return False
    else:
        if parsed.scheme != 'https':
            return False

        top_level = parsed.netloc.split('.', 1)[1]
        if '.' not in top_level:
            # the netloc does not have a subdomain
            top_level = parsed.netloc

        return top_level in ['horsereality.com', 'shay.cat']

def cors_headers(request: sanic.Request) -> dict:
    """Returns a dictionary of headers based on origin_allowed_cors."""
    origin = request.headers.get('Origin')
    if request.app.ctx.origin_allowed_cors(origin):
        return {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': origin,
        }

    return {}

app.ctx.origin_allowed_cors = origin_allowed_cors
app.ctx.cors_headers = cors_headers

@app.listener('after_server_start')
async def server_init(app: sanic.Sanic, _):
    # For v1
    app.ctx.session = aiohttp.ClientSession()

    app.ctx.hr = horsereality.Client(config['remember_cookie_name'], config['remember_cookie_value'], auto_rollover=True)
    await app.ctx.hr.verify()
    logger.info('Initialized Horse Reality client')

    if config.get('redis') is not None:
        app.ctx.redis = aioredis.Redis.from_url(config['redis'], encoding='utf-8')
    else:
        app.ctx.redis = None

    app.ctx.psql_pool = await asyncpg.create_pool(**config['postgres'])

# This dict intentionally skips a number of error
# codes that Realtools would never raise
status_code_dict = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    408: 'Request Timeout',
    413: 'Payload Too Large',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
}

@app.exception(Exception)
async def error_handler(request: sanic.Request, exception: BaseException):
    status_code = getattr(exception, 'status_code', getattr(exception, 'status', 500))
    error_name = None
    error_message = status_code_dict.get(status_code, 'Internal Server Error')

    if status_code == 500:
        traceback.print_exc()

    if isinstance(exception, horsereality.HorseRealityException):
        error_message = exception.message

    elif isinstance(exception, SanicException):
        error_message = str(exception)
        error_name = (exception.extra or {}).get('name')

    return r.json(
        {'status': status_code, 'message': error_message, 'name': error_name},
        status=status_code,
        headers=request.app.ctx.cors_headers(request),
    )

run_address = config.get('address', 'localhost')
run_port = config.get('port', 2965)
app.run(run_address, run_port, debug=debug, auto_reload=debug)
