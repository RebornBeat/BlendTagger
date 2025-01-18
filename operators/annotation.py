import bpy
import bmesh
from bpy.props import StringProperty, IntProperty, FloatVectorProperty
from bpy.types import Operator

class BLENDTAGGER_OT_add_tag(Operator):
    """Add a new tag to the active object"""
    bl_idname = "blendtagger.add_tag"
    bl_label = "Add Tag"
    bl_options = {'REGISTER', 'UNDO'}

    tag_name: StringProperty(
        name="Tag Name",
        description="Name of the tag to add"
    )

    tag_color: FloatVectorProperty(
        name="Tag Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0
    )

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Add new tag
        tag = obj.blendtagger.tags.add()
        tag.name = self.tag_name
        tag.color = self.tag_color

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class BLENDTAGGER_OT_remove_tag(Operator):
    """Remove a tag from the active object"""
    bl_idname = "blendtagger.remove_tag"
    bl_label = "Remove Tag"
    bl_options = {'REGISTER', 'UNDO'}

    tag_name: StringProperty(
        name="Tag Name",
        description="Name of the tag to remove"
    )

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {'CANCELLED'}

        # Find and remove tag
        for i, tag in enumerate(obj.blendtagger.tags):
            if tag.name == self.tag_name:
                obj.blendtagger.tags.remove(i)
                break

        return {'FINISHED'}

class BLENDTAGGER_OT_add_mesh_annotation(Operator):
    """Add annotation to selected mesh components"""
    bl_idname = "blendtagger.add_mesh_annotation"
    bl_label = "Add Mesh Annotation"
    bl_options = {'REGISTER', 'UNDO'}

    tag: StringProperty(
        name="Tag",
        description="Tag for the mesh annotation"
    )

    def execute(self, context):
        obj = context.active_object
        if obj.type != 'MESH' or obj.mode != 'EDIT':
            self.report({'ERROR'}, "Must be in edit mode on a mesh object")
            return {'CANCELLED'}

        # Get bmesh for current edit mode mesh
        bm = bmesh.from_edit_mesh(obj.data)

        # Create new annotation
        annotation = obj.blendtagger.mesh_annotations.add()
        annotation.tag = self.tag

        # Store selected elements based on selection mode
        if context.tool_settings.mesh_select_mode[0]:  # Vertices
            for vert in bm.verts:
                if vert.select:
                    idx = annotation.vertex_indices.add()
                    idx.value = vert.index

        elif context.tool_settings.mesh_select_mode[1]:  # Edges
            for edge in bm.edges:
                if edge.select:
                    idx = annotation.edge_indices.add()
                    idx.value = edge.index

        elif context.tool_settings.mesh_select_mode[2]:  # Faces
            for face in bm.faces:
                if face.select:
                    idx = annotation.face_indices.add()
                    idx.value = face.index

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class BLENDTAGGER_OT_remove_mesh_annotation(Operator):
    """Remove a mesh annotation"""
    bl_idname = "blendtagger.remove_mesh_annotation"
    bl_label = "Remove Mesh Annotation"
    bl_options = {'REGISTER', 'UNDO'}

    annotation_index: IntProperty(
        name="Annotation Index",
        description="Index of the annotation to remove"
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}

        if self.annotation_index >= 0 and self.annotation_index < len(obj.blendtagger.mesh_annotations):
            obj.blendtagger.mesh_annotations.remove(self.annotation_index)

        return {'FINISHED'}

class BLENDTAGGER_OT_select_annotation(Operator):
    """Select mesh elements from annotation"""
    bl_idname = "blendtagger.select_annotation"
    bl_label = "Select Annotation"
    bl_options = {'REGISTER', 'UNDO'}

    annotation_index: IntProperty(
        name="Annotation Index",
        description="Index of the annotation to select"
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}

        # Ensure we're in edit mode
        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        annotation = obj.blendtagger.mesh_annotations[self.annotation_index]
        bm = bmesh.from_edit_mesh(obj.data)

        # Deselect all first
        for v in bm.verts: v.select = False
        for e in bm.edges: e.select = False
        for f in bm.faces: f.select = False

        # Select based on stored indices
        for idx in annotation.vertex_indices:
            if idx.value < len(bm.verts):
                bm.verts[idx.value].select = True

        for idx in annotation.edge_indices:
            if idx.value < len(bm.edges):
                bm.edges[idx.value].select = True

        for idx in annotation.face_indices:
            if idx.value < len(bm.faces):
                bm.faces[idx.value].select = True

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BLENDTAGGER_OT_add_tag)
    bpy.utils.register_class(BLENDTAGGER_OT_remove_tag)
    bpy.utils.register_class(BLENDTAGGER_OT_add_mesh_annotation)
    bpy.utils.register_class(BLENDTAGGER_OT_remove_mesh_annotation)
    bpy.utils.register_class(BLENDTAGGER_OT_select_annotation)

def unregister():
    bpy.utils.unregister_class(BLENDTAGGER_OT_select_annotation)
    bpy.utils.unregister_class(BLENDTAGGER_OT_remove_mesh_annotation)
    bpy.utils.unregister_class(BLENDTAGGER_OT_add_mesh_annotation)
    bpy.utils.unregister_class(BLENDTAGGER_OT_remove_tag)
    bpy.utils.unregister_class(BLENDTAGGER_OT_add_tag)
