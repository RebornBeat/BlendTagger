from . import annotation_store
from . import animation_store
from . import export_formats

modules = [
    annotation_store,
    animation_store,
    export_formats
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
