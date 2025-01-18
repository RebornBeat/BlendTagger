import bpy
from bpy.types import Panel

class BLENDTAGGER_PT_animation_panel(Panel):
    bl_label = "Animation Data"
    bl_idname = "BLENDTAGGER_PT_animation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendTagger'
    bl_parent_id = "BLENDTAGGER_PT_main_panel"

    @classmethod
    def poll(cls, context):
        return (context.scene.blendtagger_mode == 'ANIMATION' and
                context.active_object is not None)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if not obj.animation_data or not obj.animation_data.action:
            layout.label(text="No animation data found")
            return

        # Animation capture settings
        box = layout.box()
        box.label(text="Capture Settings")
        col = box.column()
        col.prop(context.scene, "blendtagger_capture_location", text="Location")
        col.prop(context.scene, "blendtagger_capture_rotation", text="Rotation")
        col.prop(context.scene, "blendtagger_capture_scale", text="Scale")

        # Animation range
        box = layout.box()
        box.label(text="Frame Range")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "blendtagger_start_frame", text="Start")
        row.prop(context.scene, "blendtagger_end_frame", text="End")

        # Capture controls
        box = layout.box()
        box.label(text="Capture Controls")
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("blendtagger.capture_animation", text="Capture Animation")
        row.operator("blendtagger.clear_animation", text="Clear")

        # Display captured data
        if hasattr(obj, "blendtagger") and obj.blendtagger.animation_tracks:
            box = layout.box()
            box.label(text="Captured Animation Data")

            # Track list
            for track in obj.blendtagger.animation_tracks:
                box = layout.box()
                row = box.row()
                row.label(text=f"Track: {track.name}")
                row.operator("blendtagger.remove_animation_track", text="", icon='X').track_name = track.name

                # Show keyframe count and property path
                col = box.column()
                col.label(text=f"Property: {track.property_path}")
                col.label(text=f"Keyframes: {len(track.keyframes)}")

                # Expand/collapse keyframe details
                if context.scene.blendtagger_show_keyframes:
                    sub_box = box.box()
                    for keyframe in track.keyframes:
                        row = sub_box.row()
                        row.label(text=f"Frame: {keyframe.frame}")
                        row.label(text=f"Value: {keyframe.value[0]:.3f}")
                        row.label(text=f"Type: {keyframe.interpolation}")

class BLENDTAGGER_PT_animation_analysis_panel(Panel):
    bl_label = "Animation Analysis"
    bl_idname = "BLENDTAGGER_PT_animation_analysis_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendTagger'
    bl_parent_id = "BLENDTAGGER_PT_animation_panel"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (context.scene.blendtagger_mode == 'ANIMATION' and
                obj is not None and
                hasattr(obj, "blendtagger") and
                len(obj.blendtagger.animation_tracks) > 0)

    def draw(self, context):
        layout = self.layout

        # Analysis tools
        box = layout.box()
        box.label(text="Analysis Tools")

        col = box.column(align=True)
        col.operator("blendtagger.analyze_motion", text="Analyze Motion")
        col.operator("blendtagger.detect_keyframe_patterns", text="Detect Patterns")

        # Motion metrics
        if context.scene.blendtagger_motion_metrics:
            box = layout.box()
            box.label(text="Motion Metrics")
            col = box.column()

            metrics = context.scene.blendtagger_motion_metrics
            col.label(text=f"Average Velocity: {metrics.avg_velocity:.2f}")
            col.label(text=f"Peak Velocity: {metrics.peak_velocity:.2f}")
            col.label(text=f"Motion Complexity: {metrics.complexity:.2f}")

            # Motion graphs
            box = layout.box()
            box.label(text="Motion Graphs")
            box.template_preview(context.scene.blendtagger_motion_preview)

def register():
    bpy.utils.register_class(BLENDTAGGER_PT_animation_panel)
    bpy.utils.register_class(BLENDTAGGER_PT_animation_analysis_panel)

    # Register properties
    bpy.types.Scene.blendtagger_capture_location = bpy.props.BoolProperty(
        name="Capture Location",
        default=True
    )
    bpy.types.Scene.blendtagger_capture_rotation = bpy.props.BoolProperty(
        name="Capture Rotation",
        default=True
    )
    bpy.types.Scene.blendtagger_capture_scale = bpy.props.BoolProperty(
        name="Capture Scale",
        default=True
    )
    bpy.types.Scene.blendtagger_start_frame = bpy.props.IntProperty(
        name="Start Frame",
        default=1
    )
    bpy.types.Scene.blendtagger_end_frame = bpy.props.IntProperty(
        name="End Frame",
        default=250
    )
    bpy.types.Scene.blendtagger_show_keyframes = bpy.props.BoolProperty(
        name="Show Keyframe Details",
        default=False
    )

    # Analysis properties
    bpy.types.Scene.blendtagger_motion_metrics = bpy.props.PointerProperty(
        type=bpy.types.PropertyGroup
    )
    bpy.types.Scene.blendtagger_motion_preview = bpy.props.PointerProperty(
        type=bpy.types.ImagePreview
    )

def unregister():
    del bpy.types.Scene.blendtagger_motion_preview
    del bpy.types.Scene.blendtagger_motion_metrics
    del bpy.types.Scene.blendtagger_show_keyframes
    del bpy.types.Scene.blendtagger_end_frame
    del bpy.types.Scene.blendtagger_start_frame
    del bpy.types.Scene.blendtagger_capture_scale
    del bpy.types.Scene.blendtagger_capture_rotation
    del bpy.types.Scene.blendtagger_capture_location

    bpy.utils.unregister_class(BLENDTAGGER_PT_animation_analysis_panel)
    bpy.utils.unregister_class(BLENDTAGGER_PT_animation_panel)
