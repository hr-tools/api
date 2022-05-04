from sanic import Blueprint

from .merge import api as merge_api
from .vision import api as vision_api

api = Blueprint.group(merge_api, vision_api, version=1)
