import bpy
from bpy.types import Operator
from typing import Set, Dict, Any, Tuple, Optional

class BlendTaggerOperator(Operator):
    """Base class for BlendTagger operators"""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Default poll method"""
        return context.active_object is not None

    def get_active_object(self, context: bpy.types.Context) -> Optional[bpy.types.Object]:
        """Get active object with validation"""
        obj = context.active_object
        if obj is None:
            self.report({'ERROR'}, "No active object")
            return None
        if not hasattr(obj, "blendtagger"):
            self.report({'ERROR'}, "Object not initialized for BlendTagger")
            return None
        return obj

    def validate_mesh_object(self, obj: bpy.types.Object) -> bool:
        """Validate mesh object"""
        if obj.type != 'MESH':
            self.report({'ERROR'}, "Operation requires a mesh object")
            return False
        return True

    def validate_animation(self, obj: bpy.types.Object) -> bool:
        """Validate object has animation data"""
        if not obj.animation_data or not obj.animation_data.action:
            self.report({'ERROR'}, "No animation data found")
            return False
        return True

    def ensure_edit_mode(self, context: bpy.types.Context) -> bool:
        """Ensure object is in edit mode"""
        if context.active_object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        return True

class BlendTaggerModalOperator(BlendTaggerOperator):
    """Base class for modal operators"""
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

    def cleanup(self, context: bpy.types.Context) -> None:
        """Cleanup method for modal operators"""
        pass

    def cancel(self, context: bpy.types.Context) -> None:
        """Cancel method for modal operators"""
        self.cleanup(context)

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> Set[str]:
        """Default modal method"""
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

class BlendTaggerBatchOperator(BlendTaggerOperator):
    """Base class for batch operations"""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def process_object(self, obj: bpy.types.Object) -> Tuple[bool, str]:
        """Process single object - override in subclasses"""
        raise NotImplementedError

    def execute(self, context: bpy.types.Context) -> Set[str]:
        success_count = 0
        fail_count = 0

        for obj in context.selected_objects:
            success, message = self.process_object(obj)
            if success:
                success_count += 1
            else:
                fail_count += 1
                self.report({'WARNING'}, f"Failed on {obj.name}: {message}")

        if fail_count == 0:
            self.report({'INFO'}, f"Successfully processed {success_count} objects")
            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                       f"Processed {success_count} objects, {fail_count} failed")
            return {'FINISHED'} if success_count > 0 else {'CANCELLED'}

class BlendTaggerPropertyOperator(BlendTaggerOperator):
    """Base class for property operations"""
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def validate_property(self, obj: bpy.types.Object,
                         property_path: str) -> Tuple[bool, Any]:
        """Validate and get property value"""
        try:
            value = obj.path_resolve(property_path)
            return True, value
        except Exception as e:
            self.report({'ERROR'}, f"Invalid property path: {str(e)}")
            return False, None

    def set_property(self, obj: bpy.types.Object,
                    property_path: str,
                    value: Any) -> bool:
        """Set property value safely"""
        try:
            obj.path_resolve(property_path, value)
            return True
        except Exception as e:
            self.report({'ERROR'}, f"Failed to set property: {str(e)}")
            return False

def register():
    pass  # These are base classes, no registration needed

def unregister():
    pass
