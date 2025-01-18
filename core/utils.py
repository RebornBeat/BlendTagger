import bpy
import bmesh
import math
from typing import List, Dict, Any, Tuple, Set, Optional
from mathutils import Vector, Matrix

def ensure_blendtagger_data(obj: bpy.types.Object) -> None:
    """Ensure object has required BlendTagger data"""
    if not hasattr(obj, "blendtagger"):
        obj.blendtagger.tags.clear()
        obj.blendtagger.mesh_annotations.clear()
        obj.blendtagger.animation_tracks.clear()

def get_mesh_statistics(obj: bpy.types.Object) -> Dict[str, int]:
    """Get mesh component statistics"""
    if obj.type != 'MESH':
        return {}

    stats = {
        'vertices': len(obj.data.vertices),
        'edges': len(obj.data.edges),
        'faces': len(obj.data.polygons),
        'materials': len(obj.material_slots),
        'uv_layers': len(obj.data.uv_layers),
        'vertex_groups': len(obj.vertex_groups)
    }
    return stats

def get_animation_statistics(obj: bpy.types.Object) -> Dict[str, Any]:
    """Get animation data statistics"""
    if not obj.animation_data or not obj.animation_data.action:
        return {}

    action = obj.animation_data.action
    stats = {
        'name': action.name,
        'frame_range': tuple(action.frame_range),
        'frame_count': int(action.frame_range[1] - action.frame_range[0] + 1),
        'fcurves': len(action.fcurves),
        'properties': set(fc.data_path for fc in action.fcurves)
    }
    return stats

def get_selected_components(obj: bpy.types.Object) -> Dict[str, List[int]]:
    """Get currently selected mesh components"""
    if obj.type != 'MESH' or obj.mode != 'EDIT':
        return {}

    bm = bmesh.from_edit_mesh(obj.data)
    return {
        'vertices': [v.index for v in bm.verts if v.select],
        'edges': [e.index for e in bm.edges if e.select],
        'faces': [f.index for f in bm.faces if f.select]
    }

def create_component_bmesh(obj: bpy.types.Object,
                         vertices: List[int] = None,
                         edges: List[int] = None,
                         faces: List[int] = None) -> bmesh.types.BMesh:
    """Create a bmesh from specified components"""
    if obj.type != 'MESH':
        return None

    bm = bmesh.new()
    mesh = obj.data

    # Create vertex lookup dictionary
    vert_lookup = {}

    # Add vertices
    if vertices:
        for v_idx in vertices:
            if v_idx < len(mesh.vertices):
                v = mesh.vertices[v_idx]
                bm_vert = bm.verts.new(v.co)
                vert_lookup[v_idx] = bm_vert

    bm.verts.ensure_lookup_table()

    # Add edges
    if edges:
        for e_idx in edges:
            if e_idx < len(mesh.edges):
                e = mesh.edges[e_idx]
                if e.vertices[0] in vert_lookup and e.vertices[1] in vert_lookup:
                    bm.edges.new((
                        vert_lookup[e.vertices[0]],
                        vert_lookup[e.vertices[1]]
                    ))

    # Add faces
    if faces:
        for f_idx in faces:
            if f_idx < len(mesh.polygons):
                f = mesh.polygons[f_idx]
                face_verts = []
                valid = True
                for v_idx in f.vertices:
                    if v_idx not in vert_lookup:
                        valid = False
                        break
                    face_verts.append(vert_lookup[v_idx])
                if valid:
                    bm.faces.new(face_verts)

    return bm

def get_component_center(obj: bpy.types.Object,
                        vertices: List[int] = None,
                        edges: List[int] = None,
                        faces: List[int] = None) -> Optional[Vector]:
    """Calculate center of selected components"""
    if obj.type != 'MESH':
        return None

    positions = []
    mesh = obj.data

    if vertices:
        positions.extend(mesh.vertices[i].co for i in vertices if i < len(mesh.vertices))

    if edges:
        for e_idx in edges:
            if e_idx < len(mesh.edges):
                edge = mesh.edges[e_idx]
                center = (mesh.vertices[edge.vertices[0]].co +
                         mesh.vertices[edge.vertices[1]].co) / 2
                positions.append(center)

    if faces:
        for f_idx in faces:
            if f_idx < len(mesh.polygons):
                face = mesh.polygons[f_idx]
                center = face.center
                positions.append(center)

    if not positions:
        return None

    return sum(positions, Vector()) / len(positions)

def interpolate_keyframes(keyframe1: Dict[str, Any],
                         keyframe2: Dict[str, Any],
                         factor: float) -> Dict[str, Any]:
    """Interpolate between two keyframes"""
    value = None
    if isinstance(keyframe1['value'], (float, int)):
        value = keyframe1['value'] + factor * (keyframe2['value'] - keyframe1['value'])
    elif isinstance(keyframe1['value'], (list, tuple)):
        value = [
            v1 + factor * (v2 - v1)
            for v1, v2 in zip(keyframe1['value'], keyframe2['value'])
        ]

    return {
        'frame': int(keyframe1['frame'] + factor * (keyframe2['frame'] - keyframe1['frame'])),
        'value': value,
        'interpolation': keyframe1['interpolation']
    }

def get_keyframe_handles(keyframe: Dict[str, Any]) -> Tuple[Vector, Vector]:
    """Get keyframe handle positions"""
    if 'handle_left' not in keyframe or 'handle_right' not in keyframe:
        # Default to linear handles
        frame = float(keyframe['frame'])
        value = float(keyframe['value'] if isinstance(keyframe['value'], (float, int))
                     else keyframe['value'][0])
        return (
            Vector((frame - 1.0, value)),
            Vector((frame + 1.0, value))
        )

    return (
        Vector(keyframe['handle_left']),
        Vector(keyframe['handle_right'])
    )

def register():
    pass  # No registration needed for utility functions

def unregister():
    pass
