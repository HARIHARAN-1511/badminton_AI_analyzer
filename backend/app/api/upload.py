"""
Video Upload API Endpoints
Handles video file upload and initial processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
import aiofiles
from datetime import datetime

router = APIRouter()

# Upload directory
UPLOAD_DIR = "data/uploads"
ALLOWED_EXTENSIONS = {".mp4"}
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB max

def validate_video_file(filename: str) -> bool:
    """Check if file has allowed extension"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a badminton match video for analysis.
    
    - Only MP4 format is supported
    - Maximum file size: 2GB
    - Returns a session_id for tracking analysis progress
    """
    # Validate file extension
    if not validate_video_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only MP4 files are supported."
        )
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create session directory
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save the uploaded file
    file_ext = os.path.splitext(file.filename)[1]
    video_filename = f"match_{timestamp}{file_ext}"
    video_path = os.path.join(session_dir, video_filename)
    
    try:
        # Stream file to disk to handle large files
        async with aiofiles.open(video_path, 'wb') as out_file:
            total_size = 0
            while content := await file.read(1024 * 1024):  # 1MB chunks
                total_size += len(content)
                if total_size > MAX_FILE_SIZE:
                    # Clean up partial file
                    os.remove(video_path)
                    raise HTTPException(
                        status_code=413,
                        detail="File too large. Maximum size is 2GB."
                    )
                await out_file.write(content)
        
        # Get video info
        import cv2
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.release()
        
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "filename": file.filename,
            "video_path": video_path,
            "video_info": {
                "fps": fps,
                "frame_count": frame_count,
                "duration_seconds": round(duration, 2),
                "duration_formatted": f"{int(duration // 60)}:{int(duration % 60):02d}",
                "width": width,
                "height": height
            },
            "message": "Video uploaded successfully. Ready for analysis."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading video: {str(e)}"
        )

@router.get("/upload/{session_id}/status")
async def get_upload_status(session_id: str):
    """Check if a video has been uploaded for a session"""
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Find video file in session directory
    video_files = [f for f in os.listdir(session_dir) if f.endswith('.mp4')]
    
    if not video_files:
        return {"uploaded": False}
    
    video_path = os.path.join(session_dir, video_files[0])
    
    import cv2
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    video.release()
    
    return {
        "uploaded": True,
        "filename": video_files[0],
        "duration_seconds": round(duration, 2)
    }

@router.delete("/upload/{session_id}")
async def delete_upload(session_id: str):
    """Delete an uploaded video and its session data"""
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        shutil.rmtree(session_dir)
        return {"success": True, "message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting session: {str(e)}"
        )
