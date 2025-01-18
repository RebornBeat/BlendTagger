import bpy
from typing import List, Dict, Any, Optional, Tuple
from ..core.data_types import AnimationTrack, AnimationKeyframe

class AnimationStore:
    """Manages storage and retrieval of animation data"""

    @staticmethod
    def capture_animation(obj: bpy.types.Object,
                         start_frame: int = None,
                         end_frame: int = None,
                         properties: List[str] = None) -> bool:
        """Capture animation data for specified properties"""
        if not hasattr(obj, "blendtagger") or not obj.animation_data or not obj.animation_data.action:
            return False

        # Use scene frame range if not specified
        if start_frame is None:
            start_frame = bpy.context.scene.frame_start
        if end_frame is None:
            end_frame = bpy.context.scene.frame_end

        # Default properties to capture
        if properties is None:
            properties = ['location', 'rotation_euler', 'scale']

        action = obj.animation_data.action

        # Clear existing tracks for properties we're capturing
        tracks_to_remove = []
        for i, track in enumerate(obj.blendtagger.animation_tracks):
            if any(prop in track.property_path for prop in properties):
                tracks_to_remove.append(i)
        for i in reversed(tracks_to_remove):
            obj.blendtagger.animation_tracks.remove(i)

        # Capture new animation data
        for fcurve in action.fcurves:
            if not any(prop in fcurve.data_path for prop in properties):
                continue

            track = obj.blendtagger.animation_tracks.add()
            track.name = f"{fcurve.data_path}[{fcurve.array_index}]"
            track.property_path = fcurve.data_path

            # Store keyframes within frame range
            for keyframe in fcurve.keyframe_points:
                if start_frame <= keyframe.co.x <= end_frame:
                    kf = track.keyframes.add()
                    kf.frame = int(keyframe.co.x)
                    kf.value[0] = keyframe.co.y  # Store value in first component
                    kf.interpolation = keyframe.interpolation

        return True

    @staticmethod
    def analyze_motion(obj: bpy.types.Object) -> Dict[str, Any]:
        """Analyze captured animation data"""
        if not hasattr(obj, "blendtagger"):
            return {}

        analysis = {
            'track_count': len(obj.blendtagger.animation_tracks),
            'keyframe_count': 0,
            'frame_range': (float('inf'), float('-inf')),
            'properties': set(),
            'metrics': {}
        }

        if analysis['track_count'] == 0:
            return analysis

        # Collect basic statistics
        velocities = []
        prev_frames = {}

        for track in obj.blendtagger.animation_tracks:
            analysis['properties'].add(track.property_path)
            analysis['keyframe_count'] += len(track.keyframes)

            # Update frame range
            if track.keyframes:
                first_frame = track.keyframes[0].frame
                last_frame = track.keyframes[-1].frame
                analysis['frame_range'] = (
                    min(analysis['frame_range'][0], first_frame),
                    max(analysis['frame_range'][1], last_frame)
                )

            # Calculate velocities between keyframes
            for kf in track.keyframes:
                if track.property_path in prev_frames:
                    prev_frame, prev_value = prev_frames[track.property_path]
                    time_diff = kf.frame - prev_frame
                    if time_diff > 0:
                        velocity = abs(kf.value[0] - prev_value) / time_diff
                        velocities.append(velocity)
                prev_frames[track.property_path] = (kf.frame, kf.value[0])

        # Calculate motion metrics
        if velocities:
            analysis['metrics'] = {
                'average_velocity': sum(velocities) / len(velocities),
                'peak_velocity': max(velocities),
                'min_velocity': min(velocities),
                'motion_complexity': len(velocities) / (analysis['frame_range'][1] - analysis['frame_range'][0])
            }

        return analysis

    @staticmethod
    def get_keyframe_at_frame(obj: bpy.types.Object,
                            frame: int,
                            property_path: str) -> Optional[Tuple[float, str]]:
        """Get interpolated value at specific frame"""
        if not hasattr(obj, "blendtagger"):
            return None

        for track in obj.blendtagger.animation_tracks:
            if track.property_path == property_path:
                # Find surrounding keyframes
                prev_kf = None
                next_kf = None

                for kf in track.keyframes:
                    if kf.frame <= frame:
                        prev_kf = kf
                    if kf.frame >= frame:
                        next_kf = kf
                        break

                if prev_kf is None or next_kf is None:
                    return None

                # Linear interpolation between keyframes
                if prev_kf.frame == next_kf.frame:
                    return (prev_kf.value[0], prev_kf.interpolation)

                t = (frame - prev_kf.frame) / (next_kf.frame - prev_kf.frame)
                value = prev_kf.value[0] + t * (next_kf.value[0] - prev_kf.value[0])

                return (value, prev_kf.interpolation)

        return None

    @staticmethod
    def optimize_keyframes(obj: bpy.types.Object,
                         tolerance: float = 0.001) -> int:
        """Optimize animation data by removing redundant keyframes"""
        if not hasattr(obj, "blendtagger"):
            return 0

        removed_count = 0

        for track in obj.blendtagger.animation_tracks:
            i = 1
            while i < len(track.keyframes) - 1:
                prev_kf = track.keyframes[i-1]
                curr_kf = track.keyframes[i]
                next_kf = track.keyframes[i+1]

                # Calculate expected value at current frame
                t = (curr_kf.frame - prev_kf.frame) / (next_kf.frame - prev_kf.frame)
                expected_value = prev_kf.value[0] + t * (next_kf.value[0] - prev_kf.value[0])

                # Check if current keyframe is redundant
                if abs(curr_kf.value[0] - expected_value) < tolerance:
                    track.keyframes.remove(i)
                    removed_count += 1
                else:
                    i += 1

        return removed_count

    @staticmethod
    def bake_animation(obj: bpy.types.Object,
                      frame_step: int = 1,
                      properties: List[str] = None) -> bool:
        """Bake animation to regular intervals"""
        if not hasattr(obj, "blendtagger") or not obj.animation_data:
            return False

        if properties is None:
            properties = ['location', 'rotation_euler', 'scale']

        # Get frame range from existing tracks
        frame_range = None
        for track in obj.blendtagger.animation_tracks:
            if track.keyframes:
                track_start = track.keyframes[0].frame
                track_end = track.keyframes[-1].frame
                if frame_range is None:
                    frame_range = [track_start, track_end]
                else:
                    frame_range[0] = min(frame_range[0], track_start)
                    frame_range[1] = max(frame_range[1], track_end)

        if frame_range is None:
            return False

        # Clear existing tracks
        obj.blendtagger.animation_tracks.clear()

        # Create new tracks with baked keyframes
        for prop in properties:
            fcurves = [fc for fc in obj.animation_data.action.fcurves
                      if fc.data_path == prop]

            for fc_idx, fcurve in enumerate(fcurves):
                track = obj.blendtagger.animation_tracks.add()
                track.name = f"{prop}[{fc_idx}]"
                track.property_path = prop

                # Bake keyframes at regular intervals
                for frame in range(frame_range[0], frame_range[1] + 1, frame_step):
                    value = fcurve.evaluate(frame)
                    kf = track.keyframes.add()
                    kf.frame = frame
                    kf.value[0] = value
                    kf.interpolation = 'LINEAR'

        return True

def register():
    pass  # No registration needed for this module

def unregister():
    pass
