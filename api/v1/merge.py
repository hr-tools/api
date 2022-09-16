import asyncio
import aiohttp
import base64
import datetime
from functools import partial
from io import BytesIO
import json
import os
import random
import re
import traceback
from urllib.parse import urlunparse

from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError
import sanic
from sanic import response as r

from .auth import relogin
from .utils import dissect_layer_path, key_translations, breed_translations


api = sanic.Blueprint('Merge-v1')

config = json.load(open('config.json'))
if not config.get('authentication'):
    msg = 'You must have authentication values.'
    raise ValueError(msg)
if not config['authentication'].get('com'):
    msg = 'You must have authentication data.'
    raise ValueError(msg)

output_config = config.get('output', {})
output_route = output_config.get('name', 'rendered')
output_route_multi = output_config.get('name-multi', 'rendered-multi')
output_path = output_config.get('path', 'rendered')
output_path_multi = output_config.get('path-multi', 'rendered-multi')

def get_page_image_urls(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    divs = soup.find_all('div', class_='horse_photo')
    if not divs:
        return {}

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

    return layers

def get_page_horse_meta(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    try:
        sex = soup.select('img.icon16')[0].attrs['alt'].lower()
    except IndexError:
        sex = None
    data = {
        'title': soup.title.string,
        'sex': sex
    }
    left_info = soup.select('div.horse_left .infotext .left')
    right_info = soup.select('div.horse_left .infotext .right')
    for left, right in zip(left_info, right_info):
        key = left.string.strip().lower().replace(' ', '_')
        value = (right.string or '').strip() or None

        # dutch server support
        key = key_translations.get(key, key)
        if key == 'breed':
            value = breed_translations.get(value, value)

        data[key] = value

    return data

def add_horse_reality_logo(image, *, left=False):
    logo = Image.open('static/horse-reality-logo-small.png')

    original_canvas = Image.new('RGBA', (image.width, image.height + logo.height))
    original_canvas.paste(image, (0, logo.height))

    logo_canvas = Image.new('RGBA', original_canvas.size)
    if left:
        logo_canvas.paste(logo, (0, 0))  # top left
    else:
        logo_canvas.paste(logo, (original_canvas.width - logo.width, 0))  # top right

    new_image = Image.alpha_composite(original_canvas, logo_canvas)
    return new_image

def pil_process(horse_id, bytefiles, *, multi=False, use_watermark=True, left_watermark=False):
    new_image = None
    for file in bytefiles:
        image = Image.open(BytesIO(file), formats=('PNG',))
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
        new_image = add_horse_reality_logo(new_image, left=left_watermark)

    def as_base64_data():
        bio = BytesIO()
        new_image.save(bio, format='PNG')
        b64_str = base64.b64encode(bio.getvalue())
        data_str_bytes = bytes('data:image/png;base64,', encoding='utf-8') + b64_str
        data_str = data_str_bytes.decode(encoding='utf-8')
        return data_str

    return as_base64_data()

@api.options('/merge')
async def cors_preflight_merge(request):
    return r.empty(headers={
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*'
    })

@api.options('/merge/multiple')
async def cors_preflight_merge_multiple(request):
    return r.empty(headers={
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*'
    })

#@api.post('/merge')
async def merge_single(request):
    payload = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    url = payload.get('url')
    if not url:
        return r.json({'message': 'Invalid request.'}, status=400)

    use_whites = payload.get('use_whites', True)
    if not isinstance(use_whites, bool):
        return r.json({'message': 'Invalid type for use_whites'}, status=400)

    use_watermark = payload.get('watermark', True)
    if not isinstance(use_watermark, bool):
        return r.json({'message': 'Invalid type for watermark'}, status=400)

    match = re.match(r'https:\/\/(v2\.|www\.)?horsereality\.(com)\/horses\/(\d{1,10})\/', url)
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
        return r.json({
            'message': 'This server is not supported by this instance of '
                'Realtools, or it has not been configured properly.'
        }, status=500, headers={'Access-Control-Allow-Origin': '*'})

    cookie = await relogin(request.app.ctx.hr)

    page_response = await request.app.ctx.session.get(url, headers={'Cookie': f'horsereality={cookie}'})
    if page_response.status != 200:
        cookie = await relogin(request.app.ctx.hr)
        page_response = await request.app.ctx.session.get(url, headers={'Cookie': f'horsereality={cookie}'})

    html_text = await page_response.text()

    loop = asyncio.get_event_loop()
    try:
        layers = await loop.run_in_executor(None, get_page_image_urls, html_text)
        if not layers:
            await relogin(request.app.ctx.hr)
            layers = await loop.run_in_executor(None, get_page_image_urls, html_text)

        page_title = (await loop.run_in_executor(None, get_page_horse_meta, html_text))['title']
    except:
        traceback.print_exc()
        return r.json({'message': 'Failed to get image URLs.'},
            status=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    bytefiles = {}
    for key, urls in layers.items():
        bytefiles[key] = {'foal': 'foal' in urls[0], 'bytefiles': []}
        for img_url in urls:
            if 'whites' in img_url and not use_whites:
                continue
            img_response = await request.app.ctx.session.get(f'https://www.horsereality.{tld}{img_url}')
            read = await img_response.read()
            bytefiles[key]['bytefiles'].append(read)

    paths = {}
    for key, pair in bytefiles.items():
        try:
            paths[f'{key}_url'] = await loop.run_in_executor(None, partial(
                pil_process,
                _id,
                pair['bytefiles'],
                use_watermark=use_watermark,
                left_watermark=pair.get('foal', False)
            ))
        except UnidentifiedImageError:
            return r.json({'message': 'Failed to get the right images.'},
                status=500,
                headers={'Access-Control-Allow-Origin': '*'}
            )
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

    if payload.get('return_layer_urls'):
        layer_urls = []
        for urls in layers.values():
            layer_urls += urls
    else:
        layer_urls = []
    return r.json(
        {
            'message': 'Success.',
            'name': horse_name,
            'original_url': url,
            'horse_id': _id,
            'tld': tld,
            'layer_urls': layer_urls,
            **paths
        },
        status=201,
        headers={'Access-Control-Allow-Origin': '*'}
    )

#@api.post('/layers')
async def get_layers(request):
    payload = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    url = payload.get('url')
    if not url:
        return r.json({'message': 'Invalid request.'}, status=400)

    match = re.match(r'https:\/\/(v2\.|www\.)?horsereality\.(com)\/horses\/(\d{1,10})\/', url)
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
        return r.json({'message': f'This server (.{tld}) is not supported by this instance of Realtools, or it has not been configured properly.'}, status=500)
    if authconfig.get('cookie'):
        cookie = authconfig.get('cookie')
    else:
        cookie = await relogin(request.app.ctx.hr)

    page_response = await request.app.ctx.session.get(url, headers={'Cookie': f'horsereality={cookie}'})
    if page_response.status != 200:
        cookie = await relogin(request.app.ctx.hr)
        page_response = await request.app.ctx.session.get(url, headers={'Cookie': f'horsereality={cookie}'})

    html_text = await page_response.text()
    loop = asyncio.get_event_loop()
    try:
        layers = await loop.run_in_executor(None, get_page_image_urls, html_text)
        if not layers:
            await relogin(request.app.ctx.hr)
            layers = await loop.run_in_executor(None, get_page_image_urls, html_text)

        horse_info = await loop.run_in_executor(None, get_page_horse_meta, html_text)
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

    if payload.get('use_foal') is True:
        layers_sized = layers_sized.get('foal') or layers_sized.get('adult') or layers_sized['horse']
    else:
        layers_sized = layers_sized.get('adult') or layers_sized['horse']

    try:
        horse_name = re.sub(r' - Horse Reality$', '', str(horse_info['title']))
        # HR oh-so-conveniently provides the horse's name in the title so for
        # a little flair we return it with the image
    except:
        horse_name = horse_info['title']

    return r.json(
        {
            'message': 'Success.',
            'name': horse_name,
            'id': _id,
            'key': _id,
            'tld': tld,
            'details': horse_info,
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

    url_regex = re.compile(r'https:\/\/(v2\.|www\.)?horsereality\.(com)\/upload\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z0-9]+\.png')
    bytefiles = []
    for url in urls:
        if not url:
            continue
        match = url_regex.match(url)
        if not match:
            return r.json(
                {'message': f'Incorrectly formatted URL at position {urls.index(url)}.'},
                status=400,
                headers={'Access-Control-Allow-Origin': '*'}
            )

        try:
            img_response = await request.app.ctx.session.get(url)
        except aiohttp.client_exceptions.TooManyRedirects:
            return r.json(
                {'message': f'404 when fetching URL at position {urls.index(url)}: {url}'},
                status=400,
                headers={'Access-Control-Allow-Origin': '*'}
            )
        if img_response.status >= 400:
            return r.json(
                {'message': f'{img_response.status} when fetching URL at position {urls.index(url)}: {url}'},
                status=400,
                headers={'Access-Control-Allow-Origin': '*'}
            )

        img_data = await img_response.read()
        bytefiles.append(img_data)

    loop = asyncio.get_event_loop()
    random_id = random.randint(1000000, 9999999)
    try:
        merged_url = await loop.run_in_executor(None, partial(pil_process, random_id, bytefiles, multi=True, use_watermark=payload.get('watermark', True), left_watermark='foals' in urls[0]))
    except:
        traceback.print_exc()
        return r.json(
            {'message': 'Failed to merge images.'},
            status=500,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    return r.json(
        {
            'message': 'Success.',
            'url': merged_url
        },
        status=201,
        headers={'Access-Control-Allow-Origin': '*'}
    )

@api.get(r'/multi-share/<share_id:(\d{10})>')
async def get_share(request, share_id):
    if not request.app.ctx.redis:
        return r.json({'message': 'This instance of Realtools does not support the share feature.'}, status=400)

    key = f'realmerge-multishare-{share_id}'
    share_data = await request.app.ctx.redis.get(key)
    if share_data is None:
        return r.json({'message': 'No such shared template exists.'}, status=404)

    try:
        return r.json(json.loads(share_data))
    except:
        return r.json({'message': 'Failed to load template data.'})

@api.post('/multi-share')
async def share(request):
    payload = request.json
    layers_data = payload.get('layers_data')
    if not request.app.ctx.redis:
        return r.json({'message': 'This instance of Realtools does not support the share feature.'}, status=400)
    elif not layers_data or not isinstance(layers_data, list):
        return r.json({'message': 'Missing, empty, or invalid layers_data.'}, status=400)

    expires_after = 604800  # 1 week
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_after)
    random_id = random.randint(1000000000, 9999999999)
    key = f'realmerge-multishare-{random_id}'
    await request.app.ctx.redis.set(key, json.dumps(layers_data))
    await request.app.ctx.redis.expire(key, expires_after)
    return r.json({
        'id': random_id,
        'url': urlunparse((
            request.headers.get('X-Forwarded-Proto', 'http'),
            request.headers['Host'],
            '/merge/multi',
            None,
            f'share={random_id}',
            None
        )),
        'expires': int(expires.timestamp())
    })

@api.post('/eat')
async def hungry(request):
    return r.empty()

@api.get('/meta/support')
async def credit_string(request):
    return r.text(config.get('instance_support', ''))
