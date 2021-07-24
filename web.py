import json
import traceback

import aiohttp
import aioredis
import sanic
from sanic import response as r

from api import api

config = json.load(open('config.json'))

app = sanic.Sanic('Realmerge')
app.static(f'/static', 'static')
app.blueprint(api)
app.__realmerge__version = 'v1.4'

# horsereality.com/rules section 10 seems to allow saving artwork like this
output_config = config.get('output', {})

output_path = output_config.get('path', 'rendered')
output_route = output_config.get('name', 'rendered')
if output_path is not None:
    app.static(f'/{output_route}', output_path)

output_route_multi = output_config.get('name-multi', 'rendered-multi')
output_path_multi = output_config.get('path-multi', 'rendered-multi')
if output_path_multi is not None:
    app.static(f'/{output_route_multi}', output_path_multi)

@app.listener('after_server_start')
async def init_aiohttp_session(app, loop):
    app.session = aiohttp.ClientSession()

    if config.get('redis') is not None:
        app.redis = await aioredis.create_redis_pool(config['redis'], encoding='utf-8')
    else:
        app.redis = None

@app.get('/')
async def index(request):
    contents = open('pages/index.html').read()
    return r.html(contents)

@app.get('/changelog')
async def changelog(request):
    contents = open('pages/changelog.html').read()
    return r.html(contents)

@app.get('/multi')
async def multi(request):
    if (
        request.args.get('share') and
        'Discordbot' in request.headers.get('User-Agent', '')
    ):
        # we figured embeds on share links would
        # end up being spammy in Discord chats
        return r.empty()

    contents = open('pages/multi.html').read()
    return r.html(contents)

@app.get('/favicon.ico')
async def favicon(request):
    return await r.file('static/favicon.ico')

@app.get('/firefox')
async def ext_firefox(request):
    return r.redirect('https://addons.mozilla.org/en-US/firefox/addon/realmerge')

@app.get('/chrome')
async def ext_chrome(request):
    return r.redirect('https://chrome.google.com/webstore/detail/realmerge/bbhiminbhbaknnpiabajnmjjedncpmpe')

# this dict intentionally skips a number of error codes that Realmerge would
# never raise
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
    504: 'Gateway Timeout'
}

@app.exception(Exception)
async def error_handler(request, exception):
    status_code = getattr(exception, 'status_code', 500)
    error_name = status_code_dict.get(status_code, 'Internal Server Error')

    if status_code == 404:
        if not request.url.islower():
            return r.redirect(request.url.lower())

    if status_code == 500:
        traceback.print_exc()

    if '/api/' in request.url:
        return r.json(
            {'status': status_code, 'message': error_name},
            status=status_code
        )

    contents = open('pages/error.html').read()
    contents = contents.format(error_code=status_code, error_name=error_name)
    return r.html(contents, status=status_code)

run_address = config.get('address', 'localhost')
run_port = config.get('port', 2965)
app.run(run_address, run_port)
