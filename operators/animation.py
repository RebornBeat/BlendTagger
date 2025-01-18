# operators/animation.py
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

class BLENDTAGGER_OT_capture_animation(Operator):
    """Captures animation data for the selected object"""
    bl_idname = "blendtagger.capture_animation"
    bl_label = "Capture Animation"

    include_location: BoolProperty(
        name="Include Location",
        default=True,
    )
    include_rotation: BoolProperty(
        name="Include Rotation",
        default=True,
    )
    include_scale: BoolProperty(
        name="Include Scale",
        default=True,
    )

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Get animation data
        if not obj.animation_data or not obj.animation_data.action:
            self.report({'ERROR'}, "No animation data found")
            return {'CANCELLED'}

        action = obj.animation_data.action

        # Clear existing tracks
        obj.blendtagger.animation_tracks.clear()

        # Capture fcurves based on settings
        for fcurve in action.fcurves:
            # Check if we should include this curve based on settings
            if fcurve.data_path == "location" and not self.include_location:
                continue
            if fcurve.data_path == "rotation_euler" and not self.include_rotation:
                continue
            if fcurve.data_path == "scale" and not self.include_scale:
                continue

            # Create new track
            track = obj.blendtagger.animation_tracks.add()
            track.name = f"{fcurve.data_path}[{fcurve.array_index}]"
            track.property_path = fcurve.data_path

            # Store keyframes
            for keyframe in fcurve.keyframe_points:
                kf = track.keyframes.add()
                kf.frame = int(keyframe.co.x)
                kf.value[0] = keyframe.co.y
                kf.interpolation = keyframe.interpolation

        self.report({'INFO'}, f"Captured animation data with {len(obj.blendtagger.animation_tracks)} tracks")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class BLENDTAGGER_OT_clear_animation_data(Operator):
    """Clears captured animation data"""
    bl_idname = "blendtagger.clear_animation"
    bl_label = "Clear Animation Data"

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {'CANCELLED'}

        obj.blendtagger.animation_tracks.clear()
        self.report({'INFO'}, "Cleared animation data")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BLENDTAGGER_OT_capture_animation)
    bpy.utils.register_class(BLENDTAGGER_OT_clear_animation_data)

def unregister():
    bpy.utils.unregister_class(BLENDTAGGER_OT_clear_animation_data)
    bpy.utils.unregister_class(BLENDTAGGER_OT_capture_animation)
