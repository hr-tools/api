from sanic import Blueprint

from .merge import api as merge_api
from .vision import api as vision_api
from .color import api as color_api

api = Blueprint.group(merge_api, vision_api, color_api, version=2)
