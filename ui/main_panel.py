import bpy
from bpy.types import Panel

class BLENDTAGGER_PT_main_panel(Panel):
    bl_label = "BlendTagger"
    bl_idname = "BLENDTAGGER_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendTagger'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj is None:
            layout.label(text="Select an object to annotate")
            return

        # Quick stats
        box = layout.box()
        row = box.row()
        row.label(text=f"Active: {obj.name}")
        row = box.row()
        if hasattr(obj, "blendtagger"):
            row.label(text=f"Tags: {len(obj.blendtagger.tags)}")
            if obj.type == 'MESH':
                row.label(text=f"Annotations: {len(obj.blendtagger.mesh_annotations)}")
            if obj.animation_data:
                row.label(text=f"Animation Tracks: {len(obj.blendtagger.animation_tracks)}")

        # Mode selection
        box = layout.box()
        box.label(text="Annotation Mode")
        row = box.row()
        row.prop(context.scene, "blendtagger_mode", expand=True)

class BLENDTAGGER_PT_tools_panel(Panel):
    bl_label = "Tools"
    bl_idname = "BLENDTAGGER_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendTagger'
    bl_parent_id = "BLENDTAGGER_PT_main_panel"

    def draw(self, context):
        layout = self.layout

        # Export tools
        box = layout.box()
        box.label(text="Export")
        col = box.column(align=True)
        col.operator("blendtagger.export_annotations", text="Export JSON").format = 'JSON'
        col.operator("blendtagger.export_annotations", text="Export CSV").format = 'CSV'

        # Submit to repository
        box = layout.box()
        box.label(text="Repository")
        col = box.column(align=True)
        col.operator("blendtagger.submit_annotations", text="Submit to Repository")

        # Settings
        box = layout.box()
        box.label(text="Settings")
        col = box.column(align=True)
        col.prop(context.scene, "blendtagger_api_key", text="API Key")
        col.prop(context.scene, "blendtagger_repository_url", text="Repository URL")

def register():
    bpy.utils.register_class(BLENDTAGGER_PT_main_panel)
    bpy.utils.register_class(BLENDTAGGER_PT_tools_panel)

    # Register properties
    bpy.types.Scene.blendtagger_mode = bpy.props.EnumProperty(
        items=[
            ('OBJECT', "Object", "Object-level annotation mode"),
            ('MESH', "Mesh", "Mesh component annotation mode"),
            ('ANIMATION', "Animation", "Animation data annotation mode"),
        ],
        default='OBJECT',
        name="Mode"
    )
    bpy.types.Scene.blendtagger_api_key = bpy.props.StringProperty(
        name="API Key",
        description="API key for repository submission",
        subtype='PASSWORD'
    )
    bpy.types.Scene.blendtagger_repository_url = bpy.props.StringProperty(
        name="Repository URL",
        description="URL for the annotation repository",
        default="https://api.blendtagger.com/submit"
    )

def unregister():
    del bpy.types.Scene.blendtagger_repository_url
    del bpy.types.Scene.blendtagger_api_key
    del bpy.types.Scene.blendtagger_mode

    bpy.utils.unregister_class(BLENDTAGGER_PT_tools_panel)
    bpy.utils.unregister_class(BLENDTAGGER_PT_main_panel)
