import bpy
from bpy.props import (StringProperty, CollectionProperty,
                      EnumProperty, BoolProperty, FloatVectorProperty,
                      IntProperty)
from bpy.types import PropertyGroup

class TagItem(PropertyGroup):
    """Basic tag data structure"""
    name: StringProperty(name="Tag", default="")
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0
    )

class MeshAnnotation(PropertyGroup):
    """Mesh-specific annotation data"""
    tag: StringProperty(name="Tag")
    vertex_indices: CollectionProperty(type=PropertyGroup)
    face_indices: CollectionProperty(type=PropertyGroup)
    edge_indices: CollectionProperty(type=PropertyGroup)

class AnimationKeyframe(PropertyGroup):
    """Animation keyframe data"""
    frame: IntProperty(name="Frame")
    value: FloatVectorProperty(name="Value", size=3)
    interpolation: StringProperty(name="Interpolation")

class AnimationTrack(PropertyGroup):
    """Animation track data"""
    name: StringProperty(name="Name")
    property_path: StringProperty(name="Property Path")
    keyframes: CollectionProperty(type=AnimationKeyframe)

class ObjectAnnotation(PropertyGroup):
    """Complete object annotation including mesh and animation data"""
    tags: CollectionProperty(type=TagItem)
    mesh_annotations: CollectionProperty(type=MeshAnnotation)
    animation_tracks: CollectionProperty(type=AnimationTrack)
    metadata: StringProperty(name="Metadata")  # JSON string for additional data

def register():
    classes = [
        TagItem,
        MeshAnnotation,
        AnimationKeyframe,
        AnimationTrack,
        ObjectAnnotation,
    ]
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register properties
    bpy.types.Object.blendtagger = bpy.props.PointerProperty(type=ObjectAnnotation)

def unregister():
    del bpy.types.Object.blendtagger

    classes = [
        ObjectAnnotation,
        AnimationTrack,
        AnimationKeyframe,
        MeshAnnotation,
        TagItem,
    ]
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
