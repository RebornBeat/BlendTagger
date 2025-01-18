import bpy
import json
import csv
import os
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy.types import Operator

class BLENDTAGGER_OT_export_annotations(Operator):
    """Export annotations to file"""
    bl_idname = "blendtagger.export_annotations"
    bl_label = "Export Annotations"

    filepath: StringProperty(
        subtype='FILE_PATH'
    )

    format: EnumProperty(
        items=[
            ('JSON', "JSON", "Export as JSON"),
            ('CSV', "CSV", "Export as CSV")
        ],
        name="Format",
        default='JSON'
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

    def gather_object_data(self, obj):
        """Gather all annotation data for an object"""
        data = {
            "name": obj.name,
            "type": obj.type,
            "tags": [{"name": tag.name, "color": list(tag.color)} for tag in obj.blendtagger.tags],
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale)
        }

        # Add mesh annotations if enabled
        if self.include_mesh and obj.type == 'MESH':
            data["mesh_annotations"] = []
            for ann in obj.blendtagger.mesh_annotations:
                mesh_ann = {
                    "tag": ann.tag,
                    "vertices": [idx.value for idx in ann.vertex_indices],
                    "edges": [idx.value for idx in ann.edge_indices],
                    "faces": [idx.value for idx in ann.face_indices]
                }
                data["mesh_annotations"].append(mesh_ann)

        # Add animation data if enabled
        if self.include_animation and obj.animation_data:
            data["animation_tracks"] = []
            for track in obj.blendtagger.animation_tracks:
                anim_track = {
                    "name": track.name,
                    "property": track.property_path,
                    "keyframes": [
                        {
                            "frame": kf.frame,
                            "value": list(kf.value),
                            "interpolation": kf.interpolation
                        }
                        for kf in track.keyframes
                    ]
                }
                data["animation_tracks"].append(anim_track)

        return data

    def export_json(self, context, filepath):
        """Export annotations in JSON format"""
        data = {
            "scene": context.scene.name,
            "objects": []
        }

        # Gather data for all objects with annotations
        for obj in context.scene.objects:
            if hasattr(obj, "blendtagger") and obj.blendtagger.tags:
                obj_data = self.gather_object_data(obj)
                data["objects"].append(obj_data)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def export_csv(self, context, filepath):
        """Export annotations in CSV format"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            header = ['object_name', 'object_type', 'tag_name', 'tag_color',
                     'location_x', 'location_y', 'location_z']
            if self.include_mesh:
                header.extend(['annotation_type', 'component_indices'])
            if self.include_animation:
                header.extend(['track_name', 'property', 'keyframe_time', 'keyframe_value'])
            writer.writerow(header)

            # Write data rows
            for obj in context.scene.objects:
                if not hasattr(obj, "blendtagger") or not obj.blendtagger.tags:
                    continue

                base_row = [
                    obj.name,
                    obj.type,
                ]

                # Write tag information
                for tag in obj.blendtagger.tags:
                    row = base_row + [
                        tag.name,
                        ','.join(str(c) for c in tag.color),
                        obj.location.x,
                        obj.location.y,
                        obj.location.z
                    ]
                    writer.writerow(row)

                # Write mesh annotations if enabled
                if self.include_mesh and obj.type == 'MESH':
                    for ann in obj.blendtagger.mesh_annotations:
                        if ann.vertex_indices:
                            row = base_row + [
                                'vertex',
                                ','.join(str(idx.value) for idx in ann.vertex_indices)
                            ]
                            writer.writerow(row)
                        if ann.edge_indices:
                            row = base_row + [
                                'edge',
                                ','.join(str(idx.value) for idx in ann.edge_indices)
                            ]
                            writer.writerow(row)
                        if ann.face_indices:
                            row = base_row + [
                                'face',
                                ','.join(str(idx.value) for idx in ann.face_indices)
                            ]
                            writer.writerow(row)

                # Write animation data if enabled
                if self.include_animation and obj.animation_data:
                    for track in obj.blendtagger.animation_tracks:
                        for kf in track.keyframes:
                            row = base_row + [
                                track.name,
                                track.property_path,
                                kf.frame,
                                ','.join(str(v) for v in kf.value)
                            ]
                            writer.writerow(row)

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file path specified")
            return {'CANCELLED'}

        try:
            if self.format == 'JSON':
                self.export_json(context, self.filepath)
            else:
                self.export_csv(context, self.filepath)

            self.report({'INFO'}, f"Successfully exported annotations to {self.filepath}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        if not self.filepath:
            blend_filepath = context.blend_data.filepath
            if blend_filepath:
                self.filepath = os.path.splitext(blend_filepath)[0]
            else:
                self.filepath = os.path.join(os.path.expanduser("~"), "untitled")

            self.filepath += f"_annotations.{self.format.lower()}"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(BLENDTAGGER_OT_export_annotations)

def unregister():
    bpy.utils.unregister_class(BLENDTAGGER_OT_export_annotations)
