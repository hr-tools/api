import aiohttp
import asyncio
import base64
from bs4 import BeautifulSoup
from io import BytesIO
import json
from os.path import exists
import re
from PIL import Image
import sanic
from sanic import response as r
import traceback
from xml.sax.saxutils import escape

config = json.load(open('config.json'))
if not config.get('authentication'):
    msg = 'You must have authentication values.'
    raise ValueError(msg)
if not config['authentication'].get('com') and not config['authentication'].get('nl'):
    msg = 'You must have authentication data for .com, .nl, or both.'
    raise ValueError(msg)

output_config = config.get('output', {})
output_route = output_config.get('name', 'rendered')
output_path = output_config.get('path', 'rendered')

app = sanic.Sanic(__name__)
app.static(f'/static', 'static')
if output_path is not None:
    app.static(f'/{output_route}', output_path)
    # horsereality.com/rules section 10 seems to allow saving artwork like this

@app.listener('after_server_start')
async def init_aiohttp_session(app, loop):
    app.session = aiohttp.ClientSession()

html_escape_table = {
    '&': '&amp;',
    '"': '&quot;',
    "'": '&apos;',
    '>': '&gt;',
    '<': '&lt;',
    '{': '&#123;',
    '}': '&#125;'
}

def sanitize_name(text):
    # we don't really want people to be able to name
    # their horses arbitrary html
    return escape(text, html_escape_table)

def sneak_token(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    inputs = soup.find_all('input', attrs={'name': '_token', 'type': 'hidden'})
    try:
        token_input = inputs[0]
        token = token_input['value']
    except (IndexError, KeyError):
        msg = 'Couldn\'t fetch the required information for authenticating with Horse Reality.'
        raise Exception(msg)
    else:
        return token

async def get_laravel_csrf_token(tld):
    # HR uses the laravel framework and generates a unique token for
    # Cross-Site Request Forgery (CSRF) protection. this makes logging in a
    # bit more tedious for us but luckily it can be abstracted away by simply
    # further pretending we're a normal user; we GET v2 /login first and sneak
    # the token from the login form
    response = await app.session.get(f'https://v2.horsereality.{tld}/login')
    html_text = await response.text()
    loop = asyncio.get_event_loop()
    token = await loop.run_in_executor(None, sneak_token, html_text)
    return token
    # btw HR has very pretty error pages. big ups @ design team

async def relogin(tld):
    token = await get_laravel_csrf_token(tld)
    login_response = await app.session.post(
        f'https://v2.horsereality.{tld}/login',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            '_token': token,
            'email': config['authentication'][tld]['email'],
            'password': config['authentication'][tld]['password']
        },
        allow_redirects=False
    )
    if login_response.status != 302:
        # when redirecting is enabled, this will be 200 because the
        # client lands on /horses, but this is not what we want, because
        # then the location header is not present. we could also check if
        # the current page is still /login, but assuming standard HTTP
        # practices are followed, we shouldn't have to worry about the
        # status code changing suddenly
        msg = 'Invalid credentials for the .%s server.' % tld
        raise ValueError(msg)

    get_cookie_url = login_response.headers['location']
    cookie_response = await app.session.get(get_cookie_url, allow_redirects=False)
    # www.horsereality.tld/?v2_auth_token=xxx

    cookie = cookie_response.cookies['horsereality']
    # thankfully HR returns the cookie value we need
    # here so we can skip a lot of annoying decoding stuff

    config['authentication'][tld]['cookie'] = cookie.value
    # Morsels should have an `.expires` but i couldn't get that to work
    # properly (aka: i'm stupid) so we just don't deal with it

    json.dump(config, open('config.json', 'w'))
    return cookie.value

def get_page_image_urls(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    title = soup.title.string

    divs = soup.find_all('div', class_='horse_photo')
    # apparently when there is both a foal and a mare, there are two of these
    # divs, one with a 'mom' class. BS4 finds the 'mom' class first due to how
    # they're structured in the page data

    # in the future, Realmerge will probably attempt to pick them both out and
    # return both images separately

    if not divs:
        return None, []

    horse_pics_div = divs[0]
    urls = re.findall(r'\/upload\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z0-9]+\.png', str(horse_pics_div))
    # this is sort of hacky but i'd rather not figure out how to use
    # `.children` properly

    return title, urls

def pil_process(horse_id, bytefiles):
    new_image = None
    for file in bytefiles:
        image = Image.open(BytesIO(file))
        if new_image is None:
            # dynamically create a new image per horse because each horse's
            # resolution is apparently just a little different
            new_image = Image.new('RGBA', image.size)

        if new_image.size != image.size:
            # sometimes images will not be the same resolution, which causes
            # Pillow to complain. luckily we can just resize to the previous
            # image's size without really any issues
            image = image.resize(new_image.size)

        new_image = Image.alpha_composite(new_image, image)

    if new_image is None:
        msg = 'No images.'
        raise ValueError(msg)

    def as_base64_data():
        bio = BytesIO()
        new_image.save(bio, format='PNG')
        b64_str = base64.b64encode(bio.getvalue())
        data_str_bytes = bytes(f'data:image/png;base64,', encoding='utf-8') + b64_str
        data_str = data_str_bytes.decode(encoding='utf-8')
        return data_str

    if output_path is None:
        # this instance's config said not to save images locally
        return as_base64_data()

    try:
        local_route = f'{output_path}/{horse_id}.png'
        new_image.save(local_route)
    except PermissionError:
        # couldn't save to local path (fix ur perms!), return as b64 anyway
        # this is sort of implicit but I hope most people running this app will
        # read the README and figure out the problem if they don't want this
        return as_base64_data()

    web_route = f'/{output_route}/{horse_id}.png'
    return web_route

@app.options('/api/merge')
async def cors_headers_return(request):
    return r.empty(headers={
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Origin': '*'
    })

@app.post('/api/merge')
async def page_process(request):
    payload = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    url = payload.get('url')
    if not url:
        return r.json({'message': 'Invalid request.'}, status=400)

    match = re.match(r'https:\/\/(v2\.|www\.)?horsereality\.(com|nl)\/horses\/(\d{3,10})\/', url)
    # we require a trailing slash here because without it HR will redirect us
    # infinity times between v2 and www. this has been reported to deloryan

    # it's a bit of a lazy solution (a slash could be appended systematically)
    # but hey whatever

    if not match:
        return r.json({'message': 'Invalid URL.'}, status=400)

    _id = match.group(3)
    tld = match.group(2)

    # check if we've already merged this horse
    # this might cause issues if the same horse ever changes appearance,
    # i'm not sure how that works exactly. maybe a checkbox could be added to
    # merge anyway
    if output_path is None or exists(f'{output_path}/{_id}.png'):
        pass
    else:
        # unfortunately we don't get to return the title like this since we
        # never actually fetch the page, but it's just flair anyway. you could
        # parse it from the URL but that would be spotty at best since it's
        # not actually required
        return r.json({
            'message': 'Success (already merged).',
            'name': None,
            'url': f'/{output_route}/{_id}.png',
            'original_url': url
        }, status=200, headers={'Access-Control-Allow-Origin': '*'})

    authconfig = config['authentication'].get(tld)
    if not authconfig:
        return r.json({
            'message': 'This server is not supported by this instance of '
                'Realmerge, or it has not been configured properly.'
        }, status=500, headers={'Access-Control-Allow-Origin': '*'})
    if authconfig.get('cookie'):
        cookie = authconfig.get('cookie')
    else:
        cookie = await relogin(tld)

    page_response = await app.session.get(url, headers={'Cookie': f'horsereality={cookie}'})
    if page_response.status != 200:
        cookie = await relogin(tld)
        page_response = await app.session.get(url, headers={'Cookie': f'horsereality={cookie}'})

    html_text = await page_response.text()

    loop = asyncio.get_event_loop()
    try:
        page_title, urls = await loop.run_in_executor(None, get_page_image_urls, html_text)
    except:
        traceback.print_exc()
        return r.json({'message': 'Failed to get image URLs.'},
            status=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    bytefiles = []
    for img_url in urls:
        img_response = await app.session.get(f'https://www.horsereality.{tld}{img_url}')
        read = await img_response.read()
        bytefiles.append(read)

    try:
        path = await loop.run_in_executor(None, pil_process, _id, bytefiles)
    except:
        traceback.print_exc()
        return r.json({'message': 'Failed to merge images.'},
            status=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    try:
        horse_name = re.sub(r' - Horse Reality$', '', str(page_title))
        # HR oh-so-conveniently provides the horse's name in the title so for
        # a little flair we return it with the image
    except:
        horse_name = page_title

    return r.json(
        {
            'message': 'Success.',
            'name': sanitize_name(horse_name),
            'url': path,
            'original_url': url
        },
        status=201,
        headers={'Access-Control-Allow-Origin': '*'}
    )

@app.get('/')
async def index(request):
    index_file = open('index.html').read()
    return r.html(index_file)

@app.post('/api/eat')
async def hungry(request):
    return r.empty()

@app.get('/favicon.ico')
async def favicon(request):
    return await r.file('static/favicon.ico')

@app.get('/firefox')
async def ext_firefox(request):
    return r.redirect('https://addons.mozilla.org/en-US/firefox/addon/realmerge')

@app.get('/chrome')
async def ext_chrome(request):
    return r.redirect('https://chrome.google.com/webstore/detail/realmerge/bbhiminbhbaknnpiabajnmjjedncpmpe')

app.run('0.0.0.0', 2965)
