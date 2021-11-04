import json
import traceback

import aiohttp
import asyncpg
import aioredis
import logging
import sanic
from sanic import response as r

from api import api
import predictor

config = json.load(open('config.json'))

logger = logging.getLogger('realtools')
logger.addHandler(logging.NullHandler())

if config.get('log') is not None:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=config['log'], encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

def parse_sheets_json(write_to='output.json', *, indent=2):
    all_layers = []
    parser = predictor.SheetParser()
    for breed in parser.orders.keys():
        all_layers.append({
            'breed': breed,
            'order': parser.orders[breed],
            'layers': parser.parse(breed)
        })

    if write_to:
        open(write_to, 'w+').write(json.dumps(all_layers, indent=indent))
    return all_layers

async def parse_sheets_db():
    all_layers = parse_sheets_json(write_to=None)
    pool = app.ctx.psql_pool

    await pool.execute('''
        CREATE TABLE IF NOT EXISTS orders
        (breed text, stallion text[], mare text[])
    ''')
    await pool.execute('''
        CREATE TABLE IF NOT EXISTS color_layers
        (breed text, dilution text, body_part text, stallion_id text, mare_id text, foal_id text, base_genes text, color text)
    ''')
    await pool.execute('''
        CREATE TABLE IF NOT EXISTS white_layers
        (breed text, body_part text, stallion_id text, mare_id text, foal_id text, roan bool, rab bool, roan_rab bool)
    ''')
    await pool.execute('''
        CREATE TABLE IF NOT EXISTS testable_white_layers
        (breed text, body_part text, stallion_id text, mare_id text, foal_id text, white_gene text, color text, roan bool, rab bool, roan_rab bool)
    ''')

    # don't want unnecessary duplicates so we just wipe the tables in case they already exist
    await pool.execute('TRUNCATE orders, color_layers, white_layers, testable_white_layers')

    orders = []
    color_layers = []
    white_layers = []
    testable_white_layers = []
    for breed_layers in all_layers:
        for layer_type, layers in breed_layers['layers'].items():
            if layer_type == 'colors':
                for layer in layers:
                    color_layers.append((
                        breed_layers['breed'],
                        layer['dilution'],
                        layer['body_part'],
                        layer['stallion_id'],
                        layer['mare_id'],
                        layer['foal_id'],
                        layer['base_genes'],
                        layer['color']
                    ))
            elif layer_type == 'whites':
                for layer in layers:
                    white_layers.append((
                        breed_layers['breed'],
                        layer['body_part'],
                        layer['stallion_id'],
                        layer['mare_id'],
                        layer['foal_id'],
                        layer['roan'],
                        layer['rab']
                    ))
            elif layer_type == 'testable_whites':
                for layer in layers:
                    testable_white_layers.append((
                        breed_layers['breed'],
                        layer['body_part'],
                        layer['stallion_id'],
                        layer['mare_id'],
                        layer['foal_id'],
                        layer['white_gene'],
                        layer['color'],
                        layer['roan'],
                        layer['rab']
                    ))

        orders.append((
            breed_layers['breed'],
            breed_layers['order']['stallion'],
            breed_layers['order']['mare']
        ))

    await pool.executemany(
        'INSERT INTO orders VALUES ($1, $2, $3)',
        orders
    )
    await pool.executemany(
        'INSERT INTO color_layers VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
        color_layers
    )
    await pool.executemany(
        'INSERT INTO white_layers VALUES ($1, $2, $3, $4, $5, $6, $7)',
        white_layers
    )
    await pool.executemany(
        'INSERT INTO testable_white_layers VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)',
        testable_white_layers
    )

app = sanic.Sanic('Realtools')
app.static(f'/static', 'static')
app.blueprint(api)
app.__realtools__version = 'v2.2'

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
    app.ctx.session = aiohttp.ClientSession()

    if config.get('redis') is not None:
        app.ctx.redis = await aioredis.create_redis_pool(config['redis'], encoding='utf-8')
    else:
        app.ctx.redis = None

    app.ctx.psql_pool = await asyncpg.create_pool(**config['postgres'])
    await parse_sheets_db()

@app.get('/')
async def index(request):
    contents = open('pages/index.html').read()
    return r.html(contents)

def ignore_discord_crawl(request):
    # we figured embeds on share links would
    # end up being spammy in Discord channels
    return (
        request.args.get('share') and
        'Discordbot' in request.headers.get('User-Agent', '')
    )

@app.get('/merge')
async def merge_index(request):
    if ignore_discord_crawl(request):
        return r.empty()

    contents = open('pages/merge/index.html').read()
    return r.html(contents)

@app.get('/merge/multi')
async def multi(request):
    if ignore_discord_crawl(request):
        return r.empty()

    contents = open('pages/merge/multi.html').read()
    return r.html(contents)

@app.get('/vision')
async def vision(request):
    if ignore_discord_crawl(request):
        return r.empty()

    contents = open('pages/vision/index.html').read()
    return r.html(contents)

@app.get('/vision/breeds')
async def vision_breeds(request):
    contents = open('pages/vision/breeds.html').read()
    return r.html(contents)

# backwards compatibility with old versions of the extension

@app.route('/merge/api/<api_route:slug>', methods=['POST', 'GET', 'OPTIONS'])
async def api_redirects(request, api_route):
    return r.redirect(f'/api/{api_route}', status=308)

@app.get('/merge/static/<route:string>')
async def static_redirects(request, route):
    return r.redirect(f'/static/{route}', status=308)

# meta

@app.get('/favicon.ico')
async def favicon(request):
    return await r.file('static/favicon.ico')

@app.get('/extension')
async def extension_redir(request):
    ua = request.headers.get('User-Agent', '')
    if 'Firefox' in ua:
        return r.redirect('/firefox')
    else:
        return r.redirect('/chrome')

@app.get('/firefox')
async def ext_firefox(request):
    return r.redirect('https://addons.mozilla.org/en-US/firefox/addon/realtools')

@app.get('/chrome')
async def ext_chrome(request):
    #return r.redirect('https://chrome.google.com/webstore/detail/bbhiminbhbaknnpiabajnmjjedncpmpe')
    contents = open('pages/chrome.html').read()
    return r.html(contents)

# this dict intentionally skips a number of error codes that Realtools would
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
        if isinstance(exception, KeyError) and str(exception) == 'horsereality':
            return r.json(
                {'message': 'Failed to authenticate with Horse Reality.', 'status': status_code},
                status=status_code
            )

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
