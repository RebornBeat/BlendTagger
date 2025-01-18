import bpy
from bpy.types import Panel

class BLENDTAGGER_PT_annotation_panel(Panel):
    bl_label = "Annotations"
    bl_idname = "BLENDTAGGER_PT_annotation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendTagger'
    bl_parent_id = "BLENDTAGGER_PT_main_panel"

    @classmethod
    def poll(cls, context):
        return (context.scene.blendtagger_mode in {'OBJECT', 'MESH'} and
                context.active_object is not None)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # Object-level tags section
        if context.scene.blendtagger_mode == 'OBJECT':
            self.draw_object_tags(context, layout, obj)
        else:  # MESH mode
            self.draw_mesh_annotations(context, layout, obj)

    def draw_object_tags(self, context, layout, obj):
        # Tag list
        box = layout.box()
        box.label(text="Object Tags")

        # Add tag button
        row = box.row()
        row.operator("blendtagger.add_tag", text="Add Tag")

        # Existing tags
        if hasattr(obj, "blendtagger"):
            for tag in obj.blendtagger.tags:
                row = box.row(align=True)
                row.prop(tag, "name", text="")
                row.prop(tag, "color", text="")
                op = row.operator("blendtagger.remove_tag", text="", icon='X')
                op.tag_name = tag.name

        # Tag presets
        box = layout.box()
        box.label(text="Tag Presets")
        row = box.row()
        row.template_list("BLENDTAGGER_UL_tag_presets", "",
                         context.scene, "blendtagger_tag_presets",
                         context.scene, "blendtagger_active_preset_index")
        col = row.column(align=True)
        col.operator("blendtagger.add_tag_preset", text="", icon='ADD')
        col.operator("blendtagger.remove_tag_preset", text="", icon='REMOVE')

    def draw_mesh_annotations(self, context, layout, obj):
        if obj.type != 'MESH':
            layout.label(text="Select a mesh object")
            return

        # Component selection mode
        box = layout.box()
        box.label(text="Selection Mode")
        row = box.row(align=True)
        row.prop(context.tool_settings, "mesh_select_mode", text="")

        # Annotation tools
        box = layout.box()
        box.label(text="Annotation Tools")
        col = box.column(align=True)
        col.operator("blendtagger.add_mesh_annotation", text="Add Annotation")
        col.operator("blendtagger.remove_mesh_annotation", text="Remove Annotation")

        # Existing annotations
        box = layout.box()
        box.label(text="Current Annotations")
        if hasattr(obj, "blendtagger"):
            for annotation in obj.blendtagger.mesh_annotations:
                row = box.row(align=True)
                row.label(text=annotation.tag)
                op = row.operator("blendtagger.select_annotation", text="Select")
                op.annotation_index = obj.blendtagger.mesh_annotations.find(annotation)
                op = row.operator("blendtagger.remove_mesh_annotation", text="", icon='X')
                op.annotation_index = obj.blendtagger.mesh_annotations.find(annotation)

class BLENDTAGGER_PT_visualization_panel(Panel):
    bl_label = "Visualization"
    bl_idname = "BLENDTAGGER_PT_visualization_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendTagger'
    bl_parent_id = "BLENDTAGGER_PT_annotation_panel"

    @classmethod
    def poll(cls, context):
        return (context.scene.blendtagger_mode == 'MESH' and
                context.active_object is not None and
                context.active_object.type == 'MESH')

    def draw(self, context):
        layout = self.layout

        # Visualization settings
        box = layout.box()
        box.label(text="Display Settings")
        col = box.column()
        col.prop(context.scene, "blendtagger_show_annotations", text="Show Annotations")
        col.prop(context.scene, "blendtagger_annotation_opacity", text="Opacity")

        # Display modes
        box = layout.box()
        box.label(text="Display Mode")
        row = box.row()
        row.prop(context.scene, "blendtagger_display_mode", expand=True)

def register():
    bpy.utils.register_class(BLENDTAGGER_PT_annotation_panel)
    bpy.utils.register_class(BLENDTAGGER_PT_visualization_panel)

    # Register properties
    bpy.types.Scene.blendtagger_show_annotations = bpy.props.BoolProperty(
        name="Show Annotations",
        default=True
    )
    bpy.types.Scene.blendtagger_annotation_opacity = bpy.props.FloatProperty(
        name="Annotation Opacity",
        default=0.5,
        min=0.0,
        max=1.0
    )
    bpy.types.Scene.blendtagger_display_mode = bpy.props.EnumProperty(
        items=[
            ('OVERLAY', "Overlay", "Show annotations as overlay"),
            ('SOLID', "Solid", "Show annotations as solid colors"),
            ('WIREFRAME', "Wireframe", "Show annotations in wireframe mode"),
        ],
        default='OVERLAY',
        name="Display Mode"
    )

def unregister():
    del bpy.types.Scene.blendtagger_display_mode
    del bpy.types.Scene.blendtagger_annotation_opacity
    del bpy.types.Scene.blendtagger_show_annotations

    bpy.utils.unregister_class(BLENDTAGGER_PT_visualization_panel)
    bpy.utils.unregister_class(BLENDTAGGER_PT_annotation_panel)
