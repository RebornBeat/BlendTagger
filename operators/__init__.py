from . import annotation
from . import export
from . import submission
from . import animation

modules = [
    annotation,
    export,
    submission,
    animation
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
