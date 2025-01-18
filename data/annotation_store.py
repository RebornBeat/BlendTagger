import bpy
import bmesh
from typing import List, Dict, Any, Optional
from ..core.data_types import TagItem, MeshAnnotation

class AnnotationStore:
    """Manages storage and retrieval of annotation data"""

    @staticmethod
    def add_tag(obj: bpy.types.Object, tag_name: str, color: tuple = (1.0, 1.0, 1.0)) -> Optional[TagItem]:
        """Add a new tag to an object"""
        if not hasattr(obj, "blendtagger"):
            return None

        tag = obj.blendtagger.tags.add()
        tag.name = tag_name
        tag.color = color
        return tag

    @staticmethod
    def remove_tag(obj: bpy.types.Object, tag_name: str) -> bool:
        """Remove a tag from an object"""
        if not hasattr(obj, "blendtagger"):
            return False

        for i, tag in enumerate(obj.blendtagger.tags):
            if tag.name == tag_name:
                obj.blendtagger.tags.remove(i)
                return True
        return False

    @staticmethod
    def add_mesh_annotation(obj: bpy.types.Object,
                          tag: str,
                          vertices: List[int] = None,
                          edges: List[int] = None,
                          faces: List[int] = None) -> Optional[MeshAnnotation]:
        """Add a new mesh annotation"""
        if not hasattr(obj, "blendtagger") or obj.type != 'MESH':
            return None

        annotation = obj.blendtagger.mesh_annotations.add()
        annotation.tag = tag

        # Add vertex indices
        if vertices:
            for v_idx in vertices:
                idx = annotation.vertex_indices.add()
                idx.value = v_idx

        # Add edge indices
        if edges:
            for e_idx in edges:
                idx = annotation.edge_indices.add()
                idx.value = e_idx

        # Add face indices
        if faces:
            for f_idx in faces:
                idx = annotation.face_indices.add()
                idx.value = f_idx

        return annotation

    @staticmethod
    def get_selected_components(obj: bpy.types.Object) -> Dict[str, List[int]]:
        """Get currently selected mesh components"""
        if obj.type != 'MESH' or obj.mode != 'EDIT':
            return {}

        bm = bmesh.from_edit_mesh(obj.data)
        result = {
            'vertices': [],
            'edges': [],
            'faces': []
        }

        # Get selection based on current mode
        if bpy.context.tool_settings.mesh_select_mode[0]:  # Vertex mode
            result['vertices'] = [v.index for v in bm.verts if v.select]
        if bpy.context.tool_settings.mesh_select_mode[1]:  # Edge mode
            result['edges'] = [e.index for e in bm.edges if e.select]
        if bpy.context.tool_settings.mesh_select_mode[2]:  # Face mode
            result['faces'] = [f.index for f in bm.faces if f.select]

        return result

    @staticmethod
    def select_components(obj: bpy.types.Object,
                        vertices: List[int] = None,
                        edges: List[int] = None,
                        faces: List[int] = None) -> bool:
        """Select specified mesh components"""
        if obj.type != 'MESH':
            return False

        # Ensure we're in edit mode
        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)

        # Clear current selection
        bpy.ops.mesh.select_all(action='DESELECT')

        # Select vertices
        if vertices:
            for idx in vertices:
                if idx < len(bm.verts):
                    bm.verts[idx].select = True

        # Select edges
        if edges:
            for idx in edges:
                if idx < len(bm.edges):
                    bm.edges[idx].select = True

        # Select faces
        if faces:
            for idx in faces:
                if idx < len(bm.faces):
                    bm.faces[idx].select = True

        bmesh.update_edit_mesh(obj.data)
        return True

    @staticmethod
    def get_annotation_stats(obj: bpy.types.Object) -> Dict[str, Any]:
        """Get statistics about object's annotations"""
        if not hasattr(obj, "blendtagger"):
            return {}

        stats = {
            'tag_count': len(obj.blendtagger.tags),
            'tags': [tag.name for tag in obj.blendtagger.tags],
            'mesh_annotations': len(obj.blendtagger.mesh_annotations) if obj.type == 'MESH' else 0,
            'components': {
                'vertices': 0,
                'edges': 0,
                'faces': 0
            }
        }

        # Count annotated components
        if obj.type == 'MESH':
            for ann in obj.blendtagger.mesh_annotations:
                stats['components']['vertices'] += len(ann.vertex_indices)
                stats['components']['edges'] += len(ann.edge_indices)
                stats['components']['faces'] += len(ann.face_indices)

        return stats

    @staticmethod
    def merge_annotations(obj: bpy.types.Object, tag_name: str) -> bool:
        """Merge all annotations with the same tag"""
        if not hasattr(obj, "blendtagger") or obj.type != 'MESH':
            return False

        merged = {
            'vertices': set(),
            'edges': set(),
            'faces': set()
        }

        # Collect all components with the same tag
        indices_to_remove = []
        for i, ann in enumerate(obj.blendtagger.mesh_annotations):
            if ann.tag == tag_name:
                merged['vertices'].update(idx.value for idx in ann.vertex_indices)
                merged['edges'].update(idx.value for idx in ann.edge_indices)
                merged['faces'].update(idx.value for idx in ann.face_indices)
                indices_to_remove.append(i)

        # Remove old annotations
        for i in reversed(indices_to_remove):
            obj.blendtagger.mesh_annotations.remove(i)

        # Create new merged annotation
        if any(merged.values()):
            AnnotationStore.add_mesh_annotation(
                obj,
                tag_name,
                vertices=list(merged['vertices']),
                edges=list(merged['edges']),
                faces=list(merged['faces'])
            )
            return True

        return False

def register():
    pass  # No registration needed for this module

def unregister():
    pass
