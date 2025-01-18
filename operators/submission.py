import bpy
import requests
import json
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

class BLENDTAGGER_OT_submit_annotations(Operator):
    """Submit annotations to the BlendTagger repository"""
    bl_idname = "blendtagger.submit_annotations"
    bl_label = "Submit to Repository"

    api_key: StringProperty(
        name="API Key",
        description="Your BlendTagger API key",
        subtype='PASSWORD'
    )

    repository_url: StringProperty(
        name="Repository URL",
        description="URL of the BlendTagger repository",
        default="https://api.blendtagger.com/v1/submit"
    )

    include_mesh: BoolProperty(
        name="Include Mesh Data",
        description="Include mesh component annotations",
        default=True
    )

    include_animation: BoolProperty(
        name="Include Animation Data",
        description="Include animation track data",
        default=True
    )

    def prepare_metadata(self, context):
        """Prepare metadata for submission"""
        return {
            "blender_version": bpy.app.version_string,
            "plugin_version": context.preferences.addons[__package__].bl_info.get("version", (0, 0, 0)),
            "scene_name": context.scene.name,
            "frame_range": (context.scene.frame_start, context.scene.frame_end),
            "submission_type": "full" if self.include_mesh and self.include_animation else "partial"
        }

    def gather_object_data(self, obj):
        """Gather annotation data for an object"""
        from .export import BLENDTAGGER_OT_export_annotations
        exporter = BLENDTAGGER_OT_export_annotations.gather_object_data
        return exporter(self, obj)

    def prepare_submission_data(self, context):
        """Prepare complete submission package"""
        data = {
            "metadata": self.prepare_metadata(context),
            "objects": []
        }

        # Gather data for all annotated objects
        for obj in context.scene.objects:
            if hasattr(obj, "blendtagger") and obj.blendtagger.tags:
                obj_data = self.gather_object_data(obj)
                data["objects"].append(obj_data)

        return data

    def validate_submission(self, data):
        """Validate submission data before sending"""
        if not data["objects"]:
            return False, "No annotated objects found"

        for obj in data["objects"]:
            if not obj.get("tags"):
                return False, f"Object {obj['name']} has no tags"

        return True, ""

    def execute(self, context):
        if not self.api_key:
            self.report({'ERROR'}, "API key is required")
            return {'CANCELLED'}

        # Prepare submission data
        submission_data = self.prepare_submission_data(context)

        # Validate before submission
        valid, message = self.validate_submission(submission_data)
        if not valid:
            self.report({'ERROR'}, f"Validation failed: {message}")
            return {'CANCELLED'}

        try:
            # Submit to repository
            response = requests.post(
                self.repository_url,
                json=submission_data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": f"BlendTagger/{context.preferences.addons[__package__].bl_info.get('version', (0, 0, 0))}"
                }
            )

            # Handle response
            if response.status_code == 201:
                submission_id = response.json().get('submission_id')
                self.report({'INFO'}, f"Successfully submitted annotations (ID: {submission_id})")
                return {'FINISHED'}
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                self.report({'ERROR'}, f"Submission failed: {error_msg}")
                return {'CANCELLED'}

        except requests.exceptions.RequestException as e:
            self.report({'ERROR'}, f"Connection error: {str(e)}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        # Load API key from preferences if available
        addon_prefs = context.preferences.addons[__package__].preferences
        if hasattr(addon_prefs, "api_key"):
            self.api_key = addon_prefs.api_key

        return context.window_manager.invoke_props_dialog(self)

class BLENDTAGGER_OT_check_submission_status(Operator):
    """Check the status of a previous submission"""
    bl_idname = "blendtagger.check_submission"
    bl_label = "Check Submission Status"

    submission_id: StringProperty(
        name="Submission ID",
        description="ID of the submission to check"
    )

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        api_key = getattr(addon_prefs, "api_key", "")

        if not api_key:
            self.report({'ERROR'}, "API key not found in preferences")
            return {'CANCELLED'}

        try:
            response = requests.get(
                f"https://api.blendtagger.com/v1/submissions/{self.submission_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )

            if response.status_code == 200:
                status_data = response.json()
                self.report({'INFO'}, f"Status: {status_data['status']}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to retrieve submission status")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error checking status: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(BLENDTAGGER_OT_submit_annotations)
    bpy.utils.register_class(BLENDTAGGER_OT_check_submission_status)

def unregister():
    bpy.utils.unregister_class(BLENDTAGGER_OT_check_submission_status)
    bpy.utils.unregister_class(BLENDTAGGER_OT_submit_annotations)
