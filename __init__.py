bl_info = {
    "name": "BlendTagger",
    "author": "Christian Liz-Fonts",
    "version": (0, 1),
    "blender": (2, 90, 0),
    "location": "View3D > Sidebar > BlendTagger",
    "description": "AI Annotation Tool for 3D Model Training",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
from . import core
from . import operators
from . import ui
from . import data
from . import api

modules = [
    core,
    operators,
    ui,
    data,
    api
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()

if __name__ == "__main__":
    register()
