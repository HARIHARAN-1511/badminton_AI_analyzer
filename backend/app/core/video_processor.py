"""
Video Processor
Handles video file operations: reading, frame extraction, clip generation
Optimized for CPU-only processing
"""

import cv2
import numpy as np
import os
from typing import Generator, Tuple, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class VideoInfo:
    """Video metadata"""
    path: str
    fps: float
    frame_count: int
    width: int
    height: int
    duration_seconds: float
    duration_formatted: str

class VideoProcessor:
    """
    CPU-optimized video processing for badminton match analysis.
    Handles frame extraction, clip generation, and video metadata.
    """
    
    def __init__(self, video_path: str):
        """Initialize with video file path"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.video_path = video_path
        self._video = None
        self._info = None
    
    def _open_video(self) -> cv2.VideoCapture:
        """Open video capture (lazy loading)"""
        if self._video is None or not self._video.isOpened():
            self._video = cv2.VideoCapture(self.video_path)
            if not self._video.isOpened():
                raise RuntimeError(f"Failed to open video: {self.video_path}")
        return self._video
    
    def get_video_info(self) -> Dict[str, Any]:
        """Get video metadata"""
        if self._info is None:
            video = self._open_video()
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            self._info = {
                "path": self.video_path,
                "fps": fps,
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "duration_seconds": round(duration, 2),
                "duration_formatted": f"{int(duration // 60)}:{int(duration % 60):02d}"
            }
        
        return self._info
    
    def read_frame(self, frame_number: int) -> Optional[np.ndarray]:
        """Read a specific frame by number"""
        video = self._open_video()
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = video.read()
        return frame if ret else None
    
    def read_frames_batch(self, start_frame: int, end_frame: int, 
                          step: int = 1) -> Generator[Tuple[int, np.ndarray], None, None]:
        """
        Read frames in a range with optional step
        Yields (frame_number, frame) tuples
        """
        video = self._open_video()
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for frame_num in range(start_frame, end_frame, step):
            ret, frame = video.read()
            if not ret:
                break
            yield frame_num, frame
            
            # Skip frames if step > 1
            for _ in range(step - 1):
                video.grab()
    
    def frame_generator(self, skip_frames: int = 0) -> Generator[Tuple[int, np.ndarray], None, None]:
        """
        Generator that yields all frames with optional skipping for faster processing
        Useful for CPU-bound analysis where we don't need every frame
        """
        video = self._open_video()
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        frame_count = 0
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            if frame_count % (skip_frames + 1) == 0:
                yield frame_count, frame
            
            frame_count += 1
    
    def extract_clip(self, start_frame: int, end_frame: int, 
                     output_path: str, include_audio: bool = False) -> str:
        """
        Extract a video clip between specified frames
        Optimized for CPU with H.264 encoding
        """
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        info = self.get_video_info()
        video = self._open_video()
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # CPU-friendly codec
        out = cv2.VideoWriter(
            output_path,
            fourcc,
            info['fps'],
            (info['width'], info['height'])
        )
        
        # Seek to start frame
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Write frames
        for frame_num in range(start_frame, end_frame + 1):
            ret, frame = video.read()
            if not ret:
                break
            out.write(frame)
        
        out.release()
        return output_path
    
    def get_frame_at_time(self, time_seconds: float) -> Optional[np.ndarray]:
        """Get frame at specific time in seconds"""
        info = self.get_video_info()
        frame_num = int(time_seconds * info['fps'])
        return self.read_frame(frame_num)
    
    def generate_thumbnail(self, output_path: str, 
                          time_seconds: Optional[float] = None,
                          size: Tuple[int, int] = (320, 180)) -> str:
        """Generate a thumbnail image from the video"""
        info = self.get_video_info()
        
        # Default to middle of video
        if time_seconds is None:
            time_seconds = info['duration_seconds'] / 2
        
        frame = self.get_frame_at_time(time_seconds)
        if frame is None:
            frame = self.read_frame(0)
        
        if frame is not None:
            # Resize
            thumbnail = cv2.resize(frame, size)
            # Convert BGR to RGB for saving
            thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)
            cv2.imwrite(output_path, cv2.cvtColor(thumbnail, cv2.COLOR_RGB2BGR))
        
        return output_path
    
    def detect_scene_changes(self, threshold: float = 30.0) -> list:
        """
        Detect major scene changes in video
        Useful for identifying match breaks, replays, etc.
        """
        scene_changes = []
        prev_frame = None
        
        for frame_num, frame in self.frame_generator(skip_frames=5):  # Sample every 5 frames
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, gray)
                mean_diff = np.mean(diff)
                
                if mean_diff > threshold:
                    scene_changes.append({
                        "frame": frame_num,
                        "time_seconds": frame_num / self.get_video_info()['fps'],
                        "difference": mean_diff
                    })
            
            prev_frame = gray
        
        return scene_changes
    
    def close(self):
        """Release video resources"""
        if self._video is not None:
            self._video.release()
            self._video = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
