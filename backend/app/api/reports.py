"""
Reports API Endpoints
Handles PDF report generation with comprehensive match analysis
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import json

router = APIRouter()

from app.utils.pdf_generator import PDFReportGenerator

OUTPUT_DIR = os.path.abspath("data/output")

@router.post("/report/{session_id}/generate")
async def generate_report(session_id: str):
    """
    Generate a comprehensive PDF report for the analyzed match.
    
    The report includes:
    - Match summary
    - Rally-by-rally breakdown
    - Player mistake analysis
    - Statistical graphs
    - Improvement recommendations
    """
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(
            status_code=404,
            detail="Analysis results not found. Please run analysis first."
        )
    
    # Load analysis results
    with open(results_path, "r") as f:
        results = json.load(f)
    
    # Generate PDF
    output_dir = os.path.join(OUTPUT_DIR, session_id)
    pdf_path = os.path.join(output_dir, "match_analysis_report.pdf")
    
    try:
        generator = PDFReportGenerator(results, output_dir)
        generator.generate_report(pdf_path)
        
        return {
            "success": True,
            "pdf_path": pdf_path,
            "download_url": f"/api/report/{session_id}/download"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Report generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )

@router.get("/report/{session_id}/download")
async def download_report(session_id: str):
    """Download the generated PDF report"""
    pdf_path = os.path.join(OUTPUT_DIR, session_id, "match_analysis_report.pdf")
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please generate the report first."
        )
    
    return FileResponse(
        path=pdf_path,
        filename="badminton_match_analysis_report.pdf",
        media_type="application/pdf"
    )

@router.get("/report/{session_id}/preview")
async def preview_report(session_id: str):
    """Get report preview data (what will be in the PDF)"""
    results_path = os.path.join(OUTPUT_DIR, session_id, "analysis_results.json")
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    # Generate preview summary
    preview = {
        "match_info": {
            "player_a": results.get("player_a", "Player A"),
            "player_b": results.get("player_b", "Player B"),
            "video_duration": results.get("video_info", {}).get("duration_formatted", "Unknown"),
            "total_rallies": results.get("total_rallies", 0),
            "total_mistakes": results.get("total_mistakes", 0)
        },
        "statistics_summary": results.get("statistics", {}),
        "available_graphs": list_available_graphs(os.path.join(OUTPUT_DIR, session_id)),
        "sections": [
            "Match Summary",
            "Rally-by-Rally Analysis",
            "Player A Performance",
            "Player B Performance",
            "Mistake Analysis",
            "Shot Distribution",
            "Rally Duration Analysis",
            "Landing Position Heatmaps",
            "Player Comparison",
            "Improvement Recommendations"
        ]
    }
    
    return preview

def list_available_graphs(output_dir: str) -> list:
    """List all generated graph images"""
    graphs_dir = os.path.join(output_dir, "graphs")
    if not os.path.exists(graphs_dir):
        return []
    
    return [f for f in os.listdir(graphs_dir) if f.endswith(('.png', '.jpg'))]
