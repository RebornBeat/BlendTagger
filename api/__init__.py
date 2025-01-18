from . import client
from . import endpoints

modules = [
    client,
    endpoints
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()

# API version and configuration
API_VERSION = "v1"
DEFAULT_API_URL = "https://api.blendtagger.com"
DEFAULT_TIMEOUT = 30  # seconds
