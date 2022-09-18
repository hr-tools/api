from sanic import Blueprint

from .merge import api as merge_api
from .vision import api as vision_api
from .horses import api as horses_api

api = Blueprint.group(merge_api, vision_api, horses_api, version=2)
