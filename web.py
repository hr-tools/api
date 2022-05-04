import json
import traceback

import aiohttp
import asyncpg
import logging
from redis import asyncio as aioredis

import sanic
from sanic import response as r
from sanic.exceptions import SanicException

from api import api
import horsereality

config = json.load(open('config.json'))

logger = logging.getLogger('realtools')
logger.addHandler(logging.NullHandler())

if config.get('log') is not None:
    logger.setLevel(getattr(logging, config.get('log_level', 'INFO')))
    handler = logging.FileHandler(filename=config['log'], encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

try:
    hr_email = config['authentication']['com']['email']
    hr_password = config['authentication']['com']['password']
except:
    # This is residue from when Horse Reality hosted two servers and thus needed different authentication values for each
    msg = 'You must have proper authentication values. (authentication.com.email, authentication.com.password)'
    raise ValueError(msg)

app = sanic.Sanic('Realtools')
app.blueprint(api)
app.config.FALLBACK_ERROR_FORMAT = 'json'
app.ctx.__realtools_version__ = 'v2.2'
app.ctx.realtools_config = config

@app.listener('after_server_start')
async def server_init(app, loop):
    app.ctx.hr = horsereality.Client()
    await app.ctx.hr.login(hr_email, hr_password)
    logger.info('Logged into Horse Reality')

    # For v1
    app.ctx.session = app.ctx.hr.http.session

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
async def error_handler(_, exception):
    status_code = getattr(exception, 'status_code', getattr(exception, 'status', 500))
    error_name = status_code_dict.get(status_code, 'Internal Server Error')

    if status_code == 500:
        traceback.print_exc()

    if isinstance(exception, horsereality.HorseRealityException):
        error_name = exception.message

    elif isinstance(exception, SanicException):
        error_name = str(exception)

    return r.json(
        {'status': status_code, 'message': error_name},
        status=status_code,
        headers={'Access-Control-Allow-Origin': '*'},
    )

run_address = config.get('address', 'localhost')
run_port = config.get('port', 2965)
app.run(run_address, run_port, debug=config.get('debug', False))
