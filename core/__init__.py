from . import data_types
from . import operators
from . import utils

modules = [
    data_types,
    operators,
    utils
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
