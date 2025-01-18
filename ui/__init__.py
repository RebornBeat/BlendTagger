import bpy
from . import main_panel
from . import annotation_panel
from . import animation_panel

modules = [
    main_panel,
    annotation_panel,
    animation_panel
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
