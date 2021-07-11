import asyncio
import base64
from functools import partial
from io import BytesIO
import json
import os
import random
import re
import traceback

from bs4 import BeautifulSoup
from PIL import Image
import sanic
from sanic import response as r

api = sanic.Blueprint('API', url_prefix='/api')

config = json.load(open('config.json'))
if not config.get('authentication'):
    msg = 'You must have authentication values.'
    raise ValueError(msg)
if not config['authentication'].get('com') and not config['authentication'].get('nl'):
    msg = 'You must have authentication data for .com, .nl, or both.'
    raise ValueError(msg)

output_config = config.get('output', {})
output_route = output_config.get('name', 'rendered')
output_route_multi = output_config.get('name-multi', 'rendered-multi')
output_path = output_config.get('path', 'rendered')
output_path_multi = output_config.get('path-multi', 'rendered-multi')

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

async def get_laravel_csrf_token(tld, session):
    # HR uses the laravel framework and generates a unique token for
    # Cross-Site Request Forgery (CSRF) protection. this makes logging in a
    # bit more tedious for us but luckily it can be abstracted away by simply
    # further pretending we're a normal user; we GET v2 /login first and sneak
    # the token from the login form
    response = await session.get(f'https://v2.horsereality.{tld}/login')
    html_text = await response.text()
    loop = asyncio.get_event_loop()
    token = await loop.run_in_executor(None, sneak_token, html_text)
    return token
    # btw HR has very pretty error pages. big ups @ design team

async def relogin(tld, session):
    token = await get_laravel_csrf_token(tld, session)
    login_response = await session.post(
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
    cookie_response = await session.get(get_cookie_url, allow_redirects=False)
    # www.horsereality.tld/?v2_auth_token=xxx

    cookie = cookie_response.cookies['horsereality']
    # thankfully HR returns the cookie value we need
    # here so we can skip a lot of annoying decoding stuff

    config['authentication'][tld]['cookie'] = cookie.value
    # Morsels should have an `.expires` but i couldn't get that to work
    # properly (aka: i'm stupid) so we just don't deal with it

    json.dump(config, open('config.json', 'w'))
    return cookie.value

def dissect_layer_path(path):
    layer_attrs_list = path.split('/')
    layer_object = {
        'type': layer_attrs_list[2],  # colors, whites, ...
        'horse_type': layer_attrs_list[3],  # mares, foals, ...
        'body_part': layer_attrs_list[4].title(),  # body, mane, tail, ...
        'size': layer_attrs_list[5],  # small, medium, large
        'id': layer_attrs_list[6].strip('.png'),
    }
    return layer_object

def get_page_image_urls(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    title = soup.title.string

    divs = soup.find_all('div', class_='horse_photo')

    if not divs:
        return None, {}

    # when there is both a foal and a mare, there are two 'horse_photo'
    # elements - one with a 'mom' class on the parent 'horse_photocon' element.
    # we deal with this in the following loop:
    layers = {}
    for div in divs:
        urls = re.findall(r'\/upload\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z0-9]+\.png', str(div))
        # this is sort of hacky but i'd rather not figure out how to use
        # `.children` properly

        parent_classes = div.parent['class']
        if 'foal' in parent_classes:
            layers['foal'] = urls
        else:
            # we could use 'mom' here but that just complicates dealing with
            # horses that do not have children on their page
            layers['horse'] = urls

    return title, layers

def add_horse_reality_logo(image):
    logo = Image.open('horse-reality-logo-small.png')

    original_canvas = Image.new('RGBA', (image.width, image.height + logo.height))
    original_canvas.paste(image, (0, logo.height))

    logo_canvas = Image.new('RGBA', original_canvas.size)
    logo_canvas.paste(logo, (original_canvas.width - logo.width, 0))  # top right

    new_image = Image.alpha_composite(original_canvas, logo_canvas)
    return new_image

def pil_process(horse_id, bytefiles, *, multi=False, use_watermark=True):
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

        if image.mode != 'RGBA':
            # sometimes images are opened in LA mode, which causes them
            # to not be merge-able
            image = image.convert('RGBA')

        new_image = Image.alpha_composite(new_image, image)

    if new_image is None:
        msg = 'No images.'
        raise ValueError(msg)

    if use_watermark is True:
        new_image = add_horse_reality_logo(new_image)

    def as_base64_data():
        bio = BytesIO()
        new_image.save(bio, format='PNG')
        b64_str = base64.b64encode(bio.getvalue())
        data_str_bytes = bytes('data:image/png;base64,', encoding='utf-8') + b64_str
        data_str = data_str_bytes.decode(encoding='utf-8')
        return data_str

    if multi is False:
        path = output_path
    else:
        path = output_path_multi

    if path is None:
        # this instance's config said not to save images locally
        return as_base64_data()

    try:
        local_route = f'{path}/{horse_id}.png'
        new_image.save(local_route)
    except PermissionError:
        # couldn't save to local path (fix ur perms!), return as b64 anyway
        # this is sort of implicit but I hope most people running this app will
        # read the README and figure out the problem if they don't want this
        return as_base64_data()

    if multi is False:
        route = output_route
    else:
        route = output_route_multi

    web_route = f'/{output_route}/{horse_id}.png'
    return web_route

@api.options('/merge')
async def cors_preflight_merge(request):
    return r.empty(headers={
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Origin': '*'
    })

@api.post('/merge')
async def merge_single(request):
    payload = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    url = payload.get('url')
    if not url:
        return r.json({'message': 'Invalid request.'}, status=400)

    match = re.match(r'https:\/\/(v2\.|www\.)?horsereality\.(com|nl)\/horses\/(\d{1,10})\/', url)
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
    if output_path is None or os.path.exists(f'{output_path}/{_id}.png'):
        pass
    else:
        # unfortunately we don't get to return the title like this since we
        # never actually fetch the page, but it's just flair anyway. you could
        # parse it from the URL but that would be spotty at best since it's
        # not actually required
        return r.json({
            'message': 'Success (already merged).',
            'name': None,
            'horse_url': f'/{output_route}/{_id}.png',
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
        cookie = await relogin(tld, request.app.session)

    page_response = await request.app.session.get(url, headers={'Cookie': f'horsereality={cookie}'})
    if page_response.status != 200:
        cookie = await relogin(tld, request.app.session)
        page_response = await request.app.session.get(url, headers={'Cookie': f'horsereality={cookie}'})

    html_text = await page_response.text()

    loop = asyncio.get_event_loop()
    try:
        page_title, layers = await loop.run_in_executor(None, get_page_image_urls, html_text)
    except:
        traceback.print_exc()
        return r.json({'message': 'Failed to get image URLs.'},
            status=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    bytefiles = {}
    for key, urls in layers.items():
        bytefiles[key] = []
        for img_url in urls:
            img_response = await request.app.session.get(f'https://www.horsereality.{tld}{img_url}')
            read = await img_response.read()
            bytefiles[key].append(read)

    paths = {}
    for key, bytefiles in bytefiles.items():
        try:
            paths[f'{key}_url'] = await loop.run_in_executor(None, partial(pil_process, _id, bytefiles, use_watermark=payload.get('watermark', True)))
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

    # temporary hotfix backwards compat for the extensions
    paths['url'] = paths.get('foal_url', paths.get('horse_url'))

    return r.json(
        {
            'message': 'Success.',
            'name': horse_name,
            'original_url': url,
            **paths
        },
        status=201,
        headers={'Access-Control-Allow-Origin': '*'}
    )

@api.post('/layers')
async def get_layers(request):
    payload = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    url = payload.get('url')
    if not url:
        return r.json({'message': 'Invalid request.'}, status=400)

    match = re.match(r'https:\/\/(v2\.|www\.)?horsereality\.(com|nl)\/horses\/(\d{1,10})\/', url)
    # we require a trailing slash here because without it HR will redirect us
    # infinity times between v2 and www. this has been reported to deloryan

    # it's a bit of a lazy solution (a slash could be appended systematically)
    # but hey whatever

    if not match:
        return r.json({'message': 'Invalid URL.'}, status=400)

    _id = match.group(3)
    tld = match.group(2)

    authconfig = config['authentication'].get(tld)
    if not authconfig:
        return r.json({'message': f'This server (.{tld}) is not supported by this instance of Realmerge, or it has not been configured properly.'}, status=500)
    if authconfig.get('cookie'):
        cookie = authconfig.get('cookie')
    else:
        cookie = await relogin(tld, request.app.session)

    page_response = await request.app.session.get(url, headers={'Cookie': f'horsereality={cookie}'})
    if page_response.status != 200:
        cookie = await relogin(tld, request.app.session)
        page_response = await request.app.session.get(url, headers={'Cookie': f'horsereality={cookie}'})

    html_text = await page_response.text()
    loop = asyncio.get_event_loop()
    try:
        page_title, layers = await loop.run_in_executor(None, get_page_image_urls, html_text)
    except:
        traceback.print_exc()
        return r.json({'message': 'Failed to get image URLs.'}, status=500)

    # we serve small urls as well as large urls because I was working on this
    # feature on a mobile connection and realized how long each image took to
    # load, so for the layer columns we display smaller images. the large urls
    # are then used for rendering.
    layers_sized = {}
    for horse_type, layers_urls in layers.items():
        layers_sized[horse_type] = []
        for image_path in layers_urls:
            small_image_path = image_path.replace('large', 'small')
            layer_object = dissect_layer_path(image_path)
            layer_object = {
                **layer_object,
                'key_id': f'{str(random.randint(10000, 99999))}-{layer_object["id"]}',
                'small_url': f'https://www.horsereality.{tld}{small_image_path}',
                'large_url': f'https://www.horsereality.{tld}{image_path}'
            }
            layers_sized[horse_type].append(layer_object)

    if payload['use_foal'] is True:
        layers_sized = layers_sized.get('foal') or layers_sized['horse']
    else:
        layers_sized = layers_sized['horse']

    try:
        horse_name = re.sub(r' - Horse Reality$', '', str(page_title))
        # HR oh-so-conveniently provides the horse's name in the title so for
        # a little flair we return it with the image
    except:
        horse_name = page_title

    return r.json(
        {
            'message': 'Success.',
            'name': horse_name,
            'id': _id,
            'key': _id,
            'layers': layers_sized
        },
        status=200
    )

@api.post('/merge/multiple')
async def merge_multiple(request):
    payload = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    urls = payload.get('urls')
    if not urls or not isinstance(urls, list):
        return r.json({'message': 'Invalid request.'}, status=400)

    url_regex = re.compile(r'https:\/\/(v2\.|www\.)?horsereality\.(com|nl)\/upload\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z0-9]+\.png')
    bytefiles = []
    for url in urls:
        if not url:
            continue
        match = url_regex.match(url)
        if not match:
            return r.json({'message': f'Invalid URL at position {urls.index(url)}.'})

        img_response = await request.app.session.get(url)
        img_data = await img_response.read()
        bytefiles.append(img_data)

    loop = asyncio.get_event_loop()
    random_id = random.randint(1000000, 9999999)
    try:
        merged_url = await loop.run_in_executor(None, partial(pil_process, random_id, bytefiles, multi=True, use_watermark=payload.get('watermark', True)))
    except:
        traceback.print_exc()
        return r.json({'message': 'Failed to merge images.'}, status=500)

    return r.json(
        {
            'message': 'Success.',
            'url': merged_url
        },
        status=201
    )

@api.post('/eat')
async def hungry(request):
    return r.empty()
