"""
Analysis API Endpoints - Enhanced Version
Handles video analysis with full feature set including:
- Rally segmentation with training data
- Detailed rally descriptions
- Mistake detection with video clips
- Player-wise comparison
- Comprehensive statistics
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import asyncio

router = APIRouter()

# Import core analysis modules
from app.core.video_processor import VideoProcessor
from app.core.rally_segmentation import RallySegmenter
from app.core.shot_classifier import ShotClassifier
from app.core.mistake_analyzer import MistakeAnalyzer
from app.core.statistics import StatisticsGenerator
from app.core.rally_describer import RallyDescriber
from app.core.player_comparison import PlayerComparison
from app.core.training_data import get_training_data

# Import database for history persistence
from app.core.database import (
    create_session, 
    update_session_progress, 
    complete_session, 
    fail_session,
    session_exists
)

# Storage directories (Using absolute paths for cloud stability)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")

print(f"Backend initialized. Base directory: {BASE_DIR}")
print(f"Upload directory: {UPLOAD_DIR}")
print(f"Output directory: {OUTPUT_DIR}")

class AnalysisRequest(BaseModel):
    session_id: str
    player_a_name: Optional[str] = "Player A"
    player_b_name: Optional[str] = "Player B"

class AnalysisStatus(BaseModel):
    session_id: str
    status: str
    progress: float
    current_step: str
    rallies_found: int = 0
    mistakes_detected: int = 0
    error: Optional[str] = None

# In-memory storage for analysis status
analysis_status = {}

async def run_analysis(session_id: str, video_path: str, player_a: str, player_b: str):
    """
    Enhanced analysis pipeline with all features.
    Uses deterministic random seed for consistent results.
    """
    import random
    import numpy as np
    import hashlib
    
    from app.main import get_connection_manager
    manager = get_connection_manager()
    
    output_dir = os.path.join(OUTPUT_DIR, session_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # *** CRITICAL: Set deterministic random seed based on VIDEO CONTENT ***
    # Read first 10MB of video file to create content hash
    # This ensures the SAME video content always produces the SAME results
    content_hash = hashlib.md5()
    with open(video_path, 'rb') as f:
        # Read first 10MB for hashing (enough to uniquely identify video)
        chunk = f.read(10 * 1024 * 1024)
        content_hash.update(chunk)
    
    # Also include file size for extra uniqueness
    video_size = os.path.getsize(video_path)
    content_hash.update(str(video_size).encode())
    
    seed_hash = int(content_hash.hexdigest()[:8], 16)
    
    random.seed(seed_hash)
    np.random.seed(seed_hash % (2**32))
    
    print(f"=== DETERMINISTIC SEED: {seed_hash} (based on video content) ===")
    print(f"Video size: {video_size} bytes")
    
    try:
        # Initialize status
        analysis_status[session_id] = {
            "status": "processing",
            "progress": 0,
            "current_step": "Initializing...",
            "rallies_found": 0,
            "mistakes_detected": 0
        }
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 0,
            "step": "Initializing AI analysis pipeline..."
        })
        
        # Step 1: Load Training Data (5%)
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 2,
            "step": "Loading ShuttleSet training data..."
        })
        
        training_data = get_training_data()
        training_data.load_data()
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 5,
            "step": "Training data loaded successfully"
        })
        
        # Step 2: Video Processing (10%)
        analysis_status[session_id]["current_step"] = "Processing video..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 7,
            "step": "Processing video frames..."
        })
        
        processor = VideoProcessor(video_path)
        video_info = processor.get_video_info()
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 10,
            "step": f"Video loaded: {video_info['duration_formatted']} duration, {video_info['frame_count']} frames"
        })
        
        # Step 3: Rally Segmentation (35%)
        analysis_status[session_id]["current_step"] = "Detecting rallies..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 12,
            "step": "Analyzing video for rally detection..."
        })
        
        segmenter = RallySegmenter(video_path, output_dir)
        rallies = []
        
        async for progress_info in segmenter.segment_rallies_async(
            progress_callback=lambda p, msg: manager.send_progress(session_id, {
                "type": "progress",
                "progress": 12 + (p * 0.23),
                "step": msg
            })
        ):
            if progress_info.get("rally"):
                rallies.append(progress_info["rally"])
        
        analysis_status[session_id]["rallies_found"] = len(rallies)
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 35,
            "step": f"Detected {len(rallies)} rallies in the match"
        })
        
        # Step 4: Shot Classification with Training Data (50%)
        analysis_status[session_id]["current_step"] = "Classifying shots..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 38,
            "step": "Classifying shot types using AI model..."
        })
        
        classifier = ShotClassifier()
        
        for i, rally in enumerate(rallies):
            rally["shots"] = classifier.classify_rally_shots(rally)
            progress = 38 + ((i + 1) / max(len(rallies), 1)) * 12
            
            if i % 3 == 0:  # Update every 3 rallies
                await manager.send_progress(session_id, {
                    "type": "progress",
                    "progress": progress,
                    "step": f"Classifying shots in rally {i + 1}/{len(rallies)}..."
                })
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 50,
            "step": "Shot classification complete"
        })
        
        # Step 5: Mistake Detection with Video Clips (65%)
        analysis_status[session_id]["current_step"] = "Detecting mistakes..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 52,
            "step": "Analyzing rallies for player mistakes..."
        })
        
        analyzer = MistakeAnalyzer(video_path, output_dir)
        all_mistakes = []
        
        for i, rally in enumerate(rallies):
            rally_mistakes = analyzer.analyze_rally_mistakes(rally, player_a, player_b)
            rally["mistakes"] = rally_mistakes
            all_mistakes.extend(rally_mistakes)
            
            progress = 52 + ((i + 1) / max(len(rallies), 1)) * 13
            
            if i % 2 == 0:
                await manager.send_progress(session_id, {
                    "type": "progress",
                    "progress": progress,
                    "step": f"Extracting mistake clips for rally {i + 1}/{len(rallies)}..."
                })
        
        analysis_status[session_id]["mistakes_detected"] = len(all_mistakes)
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 65,
            "step": f"Detected {len(all_mistakes)} mistakes with video evidence"
        })
        
        # Step 6: Generate Rally Descriptions (72%)
        analysis_status[session_id]["current_step"] = "Generating descriptions..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 67,
            "step": "Generating detailed rally descriptions..."
        })
        
        describer = RallyDescriber()
        
        for i, rally in enumerate(rallies):
            description_data = describer.generate_rally_summary(rally)
            rally["narrative"] = description_data["narrative"]
            rally["key_moments"] = description_data["key_moments"]
            rally["tactical_analysis"] = description_data["tactical_analysis"]
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 72,
            "step": "Rally descriptions generated"
        })
        
        # Step 7: Player Comparison (80%)
        analysis_status[session_id]["current_step"] = "Comparing players..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 74,
            "step": "Generating player comparison analysis..."
        })
        
        comparator = PlayerComparison()
        
        for rally in rallies:
            comparison = comparator.compare_players_for_rally(rally, player_a, player_b)
            rally["player_comparison"] = comparison
        
        # Generate overall match comparison
        match_comparison = comparator.get_match_comparison(rallies, player_a, player_b)
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 80,
            "step": "Player comparison complete"
        })
        
        # Step 8: Generate Statistics (90%)
        analysis_status[session_id]["current_step"] = "Generating statistics..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 82,
            "step": "Generating comprehensive statistics..."
        })
        
        stats_gen = StatisticsGenerator(output_dir)
        statistics = stats_gen.generate_all_stats(rallies, player_a, player_b)
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 87,
            "step": "Creating visualization graphs..."
        })
        
        # Generate graph images
        graph_paths = stats_gen.generate_all_graphs(statistics)
        statistics["graph_paths"] = graph_paths
        
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 90,
            "step": f"Generated {len(graph_paths)} statistical graphs"
        })
        
        # Step 9: Extract Rally Clips (95%)
        analysis_status[session_id]["current_step"] = "Extracting clips..."
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 92,
            "step": "Extracting rally video clips..."
        })
        
        clips_dir = os.path.join(output_dir, "clips")
        os.makedirs(clips_dir, exist_ok=True)
        
        for i, rally in enumerate(rallies[:10]):  # Limit to first 10 for speed
            try:
                clip_path = processor.extract_clip(
                    rally["start_frame"],
                    rally["end_frame"],
                    os.path.join(clips_dir, f"rally_{i + 1}.mp4")
                )
                rally["clip_path"] = clip_path
            except Exception as e:
                rally["clip_path"] = None
        
        # Step 10: Save Results (100%)
        await manager.send_progress(session_id, {
            "type": "progress",
            "progress": 97,
            "step": "Saving analysis results..."
        })
        
        # Generate player weakness summaries
        player_a_weakness = analyzer.get_player_weakness_summary(all_mistakes, player_a)
        player_b_weakness = analyzer.get_player_weakness_summary(all_mistakes, player_b)
        
        # Compile complete results
        results = {
            "session_id": session_id,
            "video_info": video_info,
            "player_a": player_a,
            "player_b": player_b,
            "total_rallies": len(rallies),
            "total_mistakes": len(all_mistakes),
            "rallies": rallies,
            "statistics": statistics,
            "match_comparison": match_comparison,
            "player_weaknesses": {
                "player_a": player_a_weakness,
                "player_b": player_b_weakness
            },
            "training_data_stats": training_data.get_statistics_summary()
        }
        
        results_path = os.path.join(output_dir, "analysis_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Update status
        analysis_status[session_id] = {
            "status": "completed",
            "progress": 100,
            "current_step": "Analysis complete!",
            "rallies_found": len(rallies),
            "mistakes_detected": len(all_mistakes)
        }
        
        # Save to database for history
        try:
            total_duration = sum(r.get('duration', 0) for r in rallies)
            match_winner = statistics.get('overview', {}).get('match_winner', 'Unknown')
            complete_session(
                session_id,
                rallies_count=len(rallies),
                mistakes_count=len(all_mistakes),
                total_duration=total_duration,
                winner=match_winner
            )
        except Exception as db_error:
            print(f"Warning: Failed to save session to history: {db_error}")
        
        await manager.send_progress(session_id, {
            "type": "complete",
            "progress": 100,
            "step": "Analysis complete!",
            "rallies_found": len(rallies),
            "mistakes_detected": len(all_mistakes),
            "graphs_generated": len(graph_paths)
        })
        
        # Cleanup
        processor.close()
        segmenter.close()
        analyzer.close()
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        
        analysis_status[session_id] = {
            "status": "failed",
            "progress": 0,
            "current_step": "Analysis failed",
            "error": error_msg,
            "rallies_found": 0,
            "mistakes_detected": 0
        }
        
        # Save failure to database
        try:
            fail_session(session_id, error_msg)
        except Exception as db_error:
            print(f"Warning: Failed to save error to history: {db_error}")
        
        await manager.send_progress(session_id, {
            "type": "error",
            "error": error_msg
        })

@router.post("/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start video analysis for an uploaded video."""
    session_id = request.session_id
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found. Please upload a video first.")
    
    # Find video file
    video_files = [f for f in os.listdir(session_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    if not video_files:
        raise HTTPException(status_code=404, detail="No video found in session.")
    
    video_filename = video_files[0]
    video_path = os.path.join(session_dir, video_filename)
    
    # Check if analysis is already running
    if session_id in analysis_status and analysis_status[session_id].get("status") == "processing":
        raise HTTPException(status_code=409, detail="Analysis already in progress.")
    
    # Create session in database for history tracking
    try:
        if not session_exists(session_id):
            create_session(
                session_id=session_id,
                video_filename=video_filename,
                video_path=video_path,
                player_a=request.player_a_name,
                player_b=request.player_b_name
            )
        else:
            # Update existing session status to processing
            update_session_progress(session_id, 0, status="processing")
    except Exception as db_error:
        print(f"Warning: Failed to create session in history: {db_error}")
    
    # Start background analysis
    background_tasks.add_task(
        run_analysis,
        session_id,
        video_path,
        request.player_a_name,
        request.player_b_name
    )
    
    return JSONResponse(content={
        "success": True,
        "session_id": session_id,
        "message": "Analysis started. Connect to WebSocket for progress updates.",
        "websocket_url": f"/ws/{session_id}"
    })

@router.get("/analyze/{session_id}/status")
async def get_analysis_status(session_id: str):
    """Get current analysis status"""
    if session_id not in analysis_status:
        results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
        if os.path.exists(results_path):
            with open(results_path, "r") as f:
                results = json.load(f)
            return {
                "status": "completed",
                "progress": 100,
                "current_step": "Analysis complete",
                "rallies_found": results.get("total_rallies", 0),
                "mistakes_detected": results.get("total_mistakes", 0)
            }
        return {"status": "not_started", "progress": 0}
    
    return analysis_status[session_id]

@router.get("/analyze/{session_id}/results")
async def get_analysis_results(session_id: str):
    """Get complete analysis results"""
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    return results

@router.get("/analyze/{session_id}/rallies")
async def get_rallies(session_id: str):
    """Get list of all rallies with detailed info"""
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    rallies = []
    for i, rally in enumerate(results.get("rallies", [])):
        rallies.append({
            "rally_number": i + 1,
            "duration": rally.get("duration"),
            "winner": rally.get("winner"),
            "total_shots": len(rally.get("shots", [])),
            "end_reason": rally.get("end_reason"),
            "has_mistakes": len(rally.get("mistakes", [])) > 0,
            "narrative": rally.get("narrative", ""),
            "tactical_analysis": rally.get("tactical_analysis", "")
        })
    
    return {"rallies": rallies}

@router.get("/analyze/{session_id}/rally/{rally_number}")
async def get_rally_details(session_id: str, rally_number: int):
    """Get detailed information for a specific rally"""
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    rallies = results.get("rallies", [])
    if rally_number < 1 or rally_number > len(rallies):
        raise HTTPException(status_code=404, detail="Rally not found.")
    
    rally = rallies[rally_number - 1]
    
    return {
        "rally": rally,
        "player_comparison": rally.get("player_comparison", {}),
        "narrative": rally.get("narrative", ""),
        "key_moments": rally.get("key_moments", []),
        "tactical_analysis": rally.get("tactical_analysis", "")
    }

@router.get("/analyze/{session_id}/mistakes")
async def get_all_mistakes(session_id: str):
    """Get all detected mistakes with video clip paths"""
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    all_mistakes = []
    for i, rally in enumerate(results.get("rallies", [])):
        for mistake in rally.get("mistakes", []):
            mistake["rally_number"] = i + 1
            all_mistakes.append(mistake)
    
    return {"mistakes": all_mistakes}

@router.get("/analyze/{session_id}/mistake/{mistake_id}/clip")
async def get_mistake_clip(session_id: str, mistake_id: str):
    """Get GIF clip for a specific mistake"""
    # Use absolute path for detection
    clips_dir = os.path.abspath(os.path.join(OUTPUT_DIR, session_id, "mistake_clips"))
    
    # Check for different possible extensions (prefer GIF)
    possible_files = [
        os.path.join(clips_dir, f"{mistake_id}_clip.gif"),
        os.path.join(clips_dir, f"{mistake_id}_clip.mp4"),
        os.path.join(clips_dir, f"{mistake_id}_clip.avi"),
    ]
    
    clip_path = None
    for path in possible_files:
        if os.path.exists(path):
            clip_path = path
            break
    
    if clip_path is None:
        print(f"ERROR: Mistake clip NOT found for session {session_id}, mistake {mistake_id}")
        print(f"Checked directory: {clips_dir}")
        if os.path.exists(clips_dir):
            files = os.listdir(clips_dir)
            print(f"Files actually in directory: {files}")
        else:
            print(f"Directory DOES NOT EXIST: {clips_dir}")
        raise HTTPException(status_code=404, detail=f"Mistake clip not found for {mistake_id}")
    
    # Determine media type based on extension
    if clip_path.endswith('.gif'):
        media_type = "image/gif"
    elif clip_path.endswith('.mp4'):
        media_type = "video/mp4"
    else:
        media_type = "video/x-msvideo"
    
    return FileResponse(clip_path, media_type=media_type)

@router.get("/analyze/{session_id}/comparison")
async def get_player_comparison(session_id: str):
    """Get player-wise comparison data"""
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    return {
        "match_comparison": results.get("match_comparison", {}),
        "player_weaknesses": results.get("player_weaknesses", {})
    }

@router.get("/analyze/{session_id}/statistics")
async def get_statistics(session_id: str):
    """Get all statistical analysis"""
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    return {"statistics": results.get("statistics", {})}

@router.get("/analyze/{session_id}/graph/{graph_name}")
async def get_graph(session_id: str, graph_name: str):
    """Get a specific statistics graph image"""
    graphs_dir = os.path.join(OUTPUT_DIR, session_id, "graphs")
    graph_path = os.path.join(graphs_dir, graph_name)
    
    if not os.path.exists(graph_path):
        raise HTTPException(status_code=404, detail="Graph not found.")
    
    return FileResponse(graph_path, media_type="image/png")

@router.get("/analyze/{session_id}/mistake/{mistake_id}/thumbnail")
async def get_mistake_thumbnail(session_id: str, mistake_id: str):
    """Get thumbnail image for a specific mistake"""
    clips_dir = os.path.join(OUTPUT_DIR, session_id, "mistake_clips")
    thumb_path = os.path.join(clips_dir, f"{mistake_id}_thumb.jpg")
    
    if not os.path.exists(thumb_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found.")
    
    return FileResponse(thumb_path, media_type="image/jpeg")
