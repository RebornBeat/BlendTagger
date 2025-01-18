import bpy
import json
import csv
import io
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

class ExportFormat:
    """Base class for export formats"""
    @staticmethod
    def validate_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data before export"""
        if not data.get('objects'):
            return False, "No objects found in data"
        return True, ""

    @staticmethod
    def format_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for export"""
        return data

class JSONFormat(ExportFormat):
    """JSON export format handler"""

    @staticmethod
    def format_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for JSON export"""
        formatted = {
            "format_version": "1.0",
            "blender_version": bpy.app.version_string,
            "timestamp": bpy.context.scene.get("blendtagger_export_time", ""),
            "scene": data.get("scene", ""),
            "objects": []
        }

        for obj_data in data.get("objects", []):
            formatted_obj = {
                "name": obj_data.get("name", ""),
                "type": obj_data.get("type", ""),
                "tags": [{"name": tag.get("name", ""),
                         "color": tag.get("color", [1, 1, 1])}
                        for tag in obj_data.get("tags", [])],
                "transform": {
                    "location": obj_data.get("location", [0, 0, 0]),
                    "rotation": obj_data.get("rotation", [0, 0, 0]),
                    "scale": obj_data.get("scale", [1, 1, 1])
                }
            }

            # Add mesh annotations if present
            if "mesh_annotations" in obj_data:
                formatted_obj["mesh_annotations"] = [
                    {
                        "tag": ann.get("tag", ""),
                        "components": {
                            "vertices": ann.get("vertices", []),
                            "edges": ann.get("edges", []),
                            "faces": ann.get("faces", [])
                        }
                    }
                    for ann in obj_data["mesh_annotations"]
                ]

            # Add animation data if present
            if "animation_tracks" in obj_data:
                formatted_obj["animation"] = [
                    {
                        "track_name": track.get("name", ""),
                        "property": track.get("property", ""),
                        "keyframes": [
                            {
                                "frame": kf.get("frame", 0),
                                "value": kf.get("value", [0, 0, 0]),
                                "interpolation": kf.get("interpolation", "LINEAR")
                            }
                            for kf in track.get("keyframes", [])
                        ]
                    }
                    for track in obj_data["animation_tracks"]
                ]

            formatted["objects"].append(formatted_obj)

        return formatted

    @staticmethod
    def export(data: Dict[str, Any], filepath: str) -> bool:
        """Export data in JSON format"""
        try:
            formatted_data = JSONFormat.format_data(data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2)
            return True
        except Exception as e:
            print(f"JSON export failed: {str(e)}")
            return False

class CSVFormat(ExportFormat):
    """CSV export format handler"""

    @staticmethod
    def get_headers() -> List[str]:
        """Get CSV headers"""
        return [
            "object_name",
            "object_type",
            "tag_name",
            "tag_color",
            "location_x",
            "location_y",
            "location_z",
            "annotation_type",
            "component_indices",
            "track_name",
            "property_path",
            "keyframe_frame",
            "keyframe_value",
            "keyframe_interpolation"
        ]

    @staticmethod
    def format_row(obj_data: Dict[str, Any],
                  tag: Dict[str, Any] = None,
                  annotation: Dict[str, Any] = None,
                  track: Dict[str, Any] = None,
                  keyframe: Dict[str, Any] = None) -> List[str]:
        """Format a single CSV row"""
        row = [
            obj_data.get("name", ""),
            obj_data.get("type", ""),
            tag.get("name", "") if tag else "",
            ",".join(map(str, tag.get("color", []))) if tag else "",
            str(obj_data.get("location", [0, 0, 0])[0]),
            str(obj_data.get("location", [0, 0, 0])[1]),
            str(obj_data.get("location", [0, 0, 0])[2]),
        ]

        # Add annotation data
        if annotation:
            row.extend([
                annotation.get("type", ""),
                ",".join(map(str, annotation.get("indices", [])))
            ])
        else:
            row.extend(["", ""])

        # Add animation data
        if track and keyframe:
            row.extend([
                track.get("name", ""),
                track.get("property", ""),
                str(keyframe.get("frame", 0)),
                ",".join(map(str, keyframe.get("value", []))),
                keyframe.get("interpolation", "")
            ])
        else:
            row.extend(["", "", "", "", ""])

        return row

    @staticmethod
    def export(data: Dict[str, Any], filepath: str) -> bool:
        """Export data in CSV format"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(CSVFormat.get_headers())

                for obj_data in data.get("objects", []):
                    # Write basic object and tag data
                    for tag in obj_data.get("tags", []):
                        writer.writerow(CSVFormat.format_row(obj_data, tag=tag))

                    # Write mesh annotations
                    for ann in obj_data.get("mesh_annotations", []):
                        for comp_type in ["vertices", "edges", "faces"]:
                            if ann.get(comp_type):
                                annotation = {
                                    "type": comp_type,
                                    "indices": ann[comp_type]
                                }
                                writer.writerow(CSVFormat.format_row(
                                    obj_data, annotation=annotation))

                    # Write animation data
                    for track in obj_data.get("animation_tracks", []):
                        for kf in track.get("keyframes", []):
                            writer.writerow(CSVFormat.format_row(
                                obj_data, track=track, keyframe=kf))

            return True
        except Exception as e:
            print(f"CSV export failed: {str(e)}")
            return False

def get_exporter(format_type: str) -> Optional[ExportFormat]:
    """Get appropriate exporter for format type"""
    exporters = {
        'JSON': JSONFormat,
        'CSV': CSVFormat
    }
    return exporters.get(format_type.upper())

def register():
    pass  # No registration needed for this module

def unregister():
    pass
