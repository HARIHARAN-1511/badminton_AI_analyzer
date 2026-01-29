"""
History API Endpoints
Provides access to analysis session history stored in the database.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List
import os
import json
import shutil

from app.core.database import (
    get_all_sessions, 
    get_session, 
    get_session_count,
    delete_session,
    session_exists
)

router = APIRouter()

OUTPUT_DIR = "data/output"

@router.get("/history")
async def get_history(
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    status: Optional[str] = Query(None, description="Filter by status: completed, processing, failed")
):
    """
    Get list of all analysis sessions from history.
    Returns paginated results with session metadata.
    """
    try:
        sessions = get_all_sessions(limit=limit, offset=offset, status_filter=status)
        total_count = get_session_count(status_filter=status)
        
        # Ensure output directories exist check
        for session in sessions:
            session_dir = os.path.join(OUTPUT_DIR, session['session_id'])
            session['has_results'] = os.path.exists(os.path.join(session_dir, 'analysis_results.json'))
            
            # Format dates for frontend
            if session.get('created_at'):
                session['created_at_formatted'] = session['created_at']
            if session.get('completed_at'):
                session['completed_at_formatted'] = session['completed_at']
        
        return {
            "success": True,
            "sessions": sessions,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_session_details(session_id: str):
    """
    Get detailed information for a specific session from history.
    Includes full analysis results if completed.
    """
    try:
        # Get session from database
        session = get_session(session_id)
        
        if not session:
            # Check if results exist on disk but not in DB (legacy sessions)
            results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
            if os.path.exists(results_path):
                with open(results_path, 'r') as f:
                    results = json.load(f)
                return {
                    "success": True,
                    "session": {
                        "session_id": session_id,
                        "status": "completed",
                        "legacy": True
                    },
                    "results": results
                }
            raise HTTPException(status_code=404, detail="Session not found")
        
        # If completed, load the full results
        results = None
        if session['status'] == 'completed':
            results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
            if os.path.exists(results_path):
                with open(results_path, 'r') as f:
                    results = json.load(f)
        
        return {
            "success": True,
            "session": session,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{session_id}")
async def delete_session_history(session_id: str, delete_files: bool = Query(False)):
    """
    Delete a session from history.
    Optionally also deletes associated output files.
    """
    try:
        # Check if session exists
        if not session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete from database
        deleted = delete_session(session_id)
        
        # Optionally delete output files
        files_deleted = False
        if delete_files:
            output_dir = os.path.join(OUTPUT_DIR, session_id)
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
                files_deleted = True
        
        return {
            "success": True,
            "message": f"Session {session_id} deleted",
            "files_deleted": files_deleted
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}/thumbnail")
async def get_session_thumbnail(session_id: str):
    """Get the thumbnail image for a session."""
    try:
        session = get_session(session_id)
        
        # Check for custom thumbnail
        if session and session.get('thumbnail_path'):
            if os.path.exists(session['thumbnail_path']):
                return FileResponse(session['thumbnail_path'], media_type="image/jpeg")
        
        # Fallback to first frame from output
        output_dir = os.path.join(OUTPUT_DIR, session_id)
        thumbnail_path = os.path.join(output_dir, "thumbnail.jpg")
        
        if os.path.exists(thumbnail_path):
            return FileResponse(thumbnail_path, media_type="image/jpeg")
        
        # Try to find any mistake thumbnail as fallback
        for file in os.listdir(output_dir) if os.path.exists(output_dir) else []:
            if file.endswith("_thumb.jpg"):
                return FileResponse(os.path.join(output_dir, file), media_type="image/jpeg")
        
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail="Thumbnail not available")

@router.get("/history/stats/summary")
async def get_history_stats():
    """Get summary statistics about analysis history."""
    try:
        total = get_session_count()
        completed = get_session_count(status_filter="completed")
        processing = get_session_count(status_filter="processing")
        failed = get_session_count(status_filter="failed")
        
        return {
            "success": True,
            "stats": {
                "total_sessions": total,
                "completed": completed,
                "processing": processing,
                "failed": failed
            }
        }
    except Exception as e:
        print(f"Error fetching history stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/history/scan")
async def scan_existing_sessions():
    """
    Scan the output directory for existing sessions and add them to history.
    Useful for importing legacy sessions that exist on disk but not in DB.
    """
    try:
        from app.core.database import create_session, complete_session
        
        imported_count = 0
        skipped_count = 0
        
        if not os.path.exists(OUTPUT_DIR):
            return {"success": True, "imported": 0, "skipped": 0}
        
        for session_id in os.listdir(OUTPUT_DIR):
            session_dir = os.path.join(OUTPUT_DIR, session_id)
            results_path = os.path.join(session_dir, "analysis_results.json")
            
            if os.path.isdir(session_dir) and os.path.exists(results_path):
                # Check if already in database
                if session_exists(session_id):
                    skipped_count += 1
                    continue
                
                # Load results to get metadata
                try:
                    with open(results_path, 'r') as f:
                        results = json.load(f)
                    
                    # Create session record
                    video_filename = results.get('video_info', {}).get('filename', 'Unknown')
                    player_a = results.get('player_a_name', 'Player A')
                    player_b = results.get('player_b_name', 'Player B')
                    
                    create_session(session_id, video_filename, "", player_a, player_b)
                    
                    # Mark as completed with stats
                    rallies = results.get('rallies', [])
                    mistakes = results.get('mistakes', [])
                    duration = results.get('duration', 0)
                    stats = results.get('statistics', {}).get('overview', {})
                    winner = stats.get('match_winner', 'Unknown')
                    
                    complete_session(
                        session_id,
                        rallies_count=len(rallies),
                        mistakes_count=len(mistakes),
                        total_duration=duration,
                        winner=winner
                    )
                    
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing session {session_id}: {e}")
        
        return {
            "success": True,
            "imported": imported_count,
            "skipped": skipped_count,
            "message": f"Imported {imported_count} sessions, skipped {skipped_count} existing"
        }
    except Exception as e:
        print(f"Error scanning sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
