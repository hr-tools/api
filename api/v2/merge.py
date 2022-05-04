import base64
import datetime
from dataclasses import asdict, dataclass
from functools import partial
from io import BytesIO
import json
import random
from typing import List, Optional
import traceback
from urllib.parse import urlunparse

from PIL import Image, UnidentifiedImageError
import sanic
from sanic import response as r
from sanic_ext import validate

import horsereality
from horsereality.utils import get_lifenumber_from_url

from .utils import name_color


api = sanic.Blueprint('Merge-v2')


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


def pil_process(bytefiles, *, use_watermark=True, left_watermark=False):
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

    bio = BytesIO()
    new_image.save(bio, format='PNG')
    b64_str = base64.b64encode(bio.getvalue())
    data_str_bytes = bytes('data:image/png;base64,', encoding='utf-8') + b64_str
    data_str = data_str_bytes.decode(encoding='utf-8')
    return data_str


@api.options('/merge')
@api.options('/merge/multiple')
@api.options('/layers')
async def cors_preflights(request):
    origin = request.headers.get('Origin')
    if origin in [
        'https://www.horsereality.com',
        'https://v2.horsereality.com',
    ]:
        return r.empty(
            headers={
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': origin
            }
        )

    return r.empty()


@dataclass
class MergePayload:
    url: str
    use_whites: Optional[bool] = True
    use_watermark: Optional[bool] = True
    return_color_info: Optional[bool] = False
    return_layers: Optional[bool] = False


@api.post('/merge')
@validate(json=MergePayload)
async def merge_single(request, body: MergePayload):
    """Merge Horse

    Combine the layers of a single horse by its URL.

    openapi:
    ---
    parameters:
        - name: url
          in: body
          description: The URL of the horse
          required: true
          schema:
            type: string
            example: https://www.horsereality.com/horses/1/
        - name: use_whites
          in: body
          description: Whether to include white layers on the result
          required: false
          default: true
          schema:
            type: boolean
        - name: use_watermark
          in: body
          description: Whether to include a watermark on the result
          required: false
          default: true
          schema:
            type: boolean
        - name: return_color_info
          in: body
          description: Whether to attempt to name the horse's color & genotype
          required: false
          default: false
          schema:
            type: boolean
        - name: return_layers
          in: body
          description: Whether to include the `layers` key
          required: false
          default: false
          schema:
            type: boolean
    responses:
        '200':
            description: The merged horse.
    """
    payload: dict = asdict(body)

    url: str = payload['url']
    use_whites: bool = payload['use_whites']
    use_watermark: bool = payload['use_watermark']
    return_color_info: bool = payload['return_color_info']
    return_layers: bool = payload['return_layers']

    lifenumber: int = get_lifenumber_from_url(url)
    if not lifenumber:
        return r.json({'message': 'Invalid URL.'}, status=400)

    hr: horsereality.Client = request.app.ctx.hr
    horse: horsereality.Horse = await hr.get_horse(lifenumber)

    should_use = lambda layer: not (layer.type is horsereality.LayerType.whites and not use_whites)
    bytefiles = {
        'adult': [await layer.read() for layer in horse.adult_layers if should_use(layer)],
        'foal': [await layer.read() for layer in horse.foal_layers if should_use(layer)],
    }

    image_data = {}
    for key, bytes_layers_list in bytefiles.items():
        if not bytes_layers_list:
            image_data[key] = None
            continue
        try:
            image_data[key] = await hr.loop.run_in_executor(None, partial(
                pil_process,
                bytes_layers_list,
                use_watermark=use_watermark,
                left_watermark=key == 'foal',
            ))
        except UnidentifiedImageError:
            return r.json(
                {'message': 'Failed to get the right images.'},
                status=500,
            )
        except:
            traceback.print_exc()
            return r.json(
                {'message': 'Failed to merge images.'},
                status=500,
            )

    horse_data = horse.to_dict()

    if not return_layers:
        horse_data.pop('layers')

    color_info = {}
    if return_color_info:
        try:
            data = await name_color(request.app, horse.breed, horse.layers)
        except:
            traceback.print_exc()
            data = {'errors': ['colors_failed']}
        if data is None:
            data = {'errors': ['colors_no_info_available']}

        color_info = {'color_info': data}

    return r.json(
        {
            **horse_data,
            'merged': image_data,
            **color_info,
        },
        status=200,
    )


@api.post('/layers')
async def get_layers(request):
    payload: dict = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    url: str = payload.get('url')
    if not url:
        return r.json({'message': 'Invalid request.'}, status=400)

    lifenumber: int = get_lifenumber_from_url(url)
    if not lifenumber:
        return r.json({'message': 'Invalid URL.'}, status=400)

    hr: horsereality.Client = request.app.ctx.hr
    horse: horsereality.Horse = await hr.get_horse(lifenumber)

    data = {
        'lifenumber': horse.lifenumber,
        'name': horse.name,
    }

    if payload.get('use_foal') is True:
        # prefer foal
        use_layers = horse.foal_layers or horse.layers

    elif payload.get('use_foal') is False:
        # prefer adult
        use_layers = horse.adult_layers or horse.layers

    else:
        # use whichever we are actually looking at
        use_layers =  horse.layers

    data['layers'] = list({**layer.to_dict(), 'key_id': f'{random.randint(10000, 99999)}-{layer.id}'} for layer in use_layers)

    return r.json(
        data,
        status=200,
    )


@api.post('/merge/multiple')
async def merge_multiple(request):
    payload: dict = request.json
    if not payload:
        return r.json({'message': 'Invalid request.'}, status=400)

    urls = payload.get('urls')
    if not urls or not isinstance(urls, list):
        return r.json({'message': 'Invalid request.'}, status=400)

    use_watermark: bool = payload.get('use_watermark', True)
    if not isinstance(use_watermark, bool):
        return r.json({'message': 'Invalid type for use_watermark'}, status=400)

    hr: horsereality.Client = request.app.ctx.hr

    try:
        layers = [horsereality.Layer(http=hr.http, url=url) for url in urls]
    except:
        return r.json({'message': 'One or more invalid layer URLs passed.'}, status=400)

    bytefiles = []
    for layer in layers:
        try:
            img_data = await layer.read()
        except horsereality.HTTPException as exc:
            return r.json(
                {'message': f'{exc.status} when fetching layer at position {layers.index(layer)}: {layer.path}'},
                status=400,
            )
        else:
            bytefiles.append(img_data)

    try:
        merged = await hr.loop.run_in_executor(None, partial(
            pil_process,
            bytefiles,
            use_watermark=use_watermark,
            left_watermark=layers[0].horse_type == 'foals',
        ))
    except:
        traceback.print_exc()
        return r.json({'message': 'Failed to merge images.'}, status=500)

    return r.json(
        {
            'merged': merged,
        },
        status=200
    )


@api.get(r'/multi-share/<share_id:(\d{10})>')
async def get_share_data(request, share_id):
    if not request.app.ctx.redis:
        return r.json({'message': 'This instance of Realtools does not support the share feature.'}, status=400)

    key = f'realtools-multishare-{share_id}'
    share_data = await request.app.ctx.redis.get(key)
    if share_data is None:
        return r.json({'message': 'No such share ID exists.'}, status=404)

    try:
        return r.json(json.loads(share_data))
    except:
        return r.json({'message': 'Failed to load share data.'}, status=500)


@api.post('/multi-share')
async def create_share_link(request):
    if not request.app.ctx.redis:
        return r.json({'message': 'This instance of Realtools does not support the share feature.'}, status=400)

    payload = request.json
    try:
        data = {
            'layers': payload['layers'],
            'enabled': payload['enabled'],
        }
    except KeyError:
        return r.json({'message': 'Invalid request.'}, status=400)

    expires_after = 604800  # 1 week
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_after)
    random_id = random.randint(1000000000, 9999999999)
    key = f'realtools-multishare-{random_id}'
    await request.app.ctx.redis.set(key, json.dumps(data))
    await request.app.ctx.redis.expire(key, expires_after)
    return r.json(
        {
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
        },
    )
