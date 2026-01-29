"""
Badminton Analysis Platform - FastAPI Backend
Main application entry point with WebSocket support for real-time progress updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Import routers
from app.api import upload, analysis, reports, history

# Create FastAPI application
app = FastAPI(
    title="Badminton Match Analysis Platform",
    description="AI-powered badminton match video analysis with rally segmentation, mistake detection, and performance analytics",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving video clips and images
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/output", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")
app.mount("/output", StaticFiles(directory="data/output"), name="output")

# Include API routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(history.router, prefix="/api", tags=["History"])

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_progress(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time analysis progress updates"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive, receive any messages from client
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)

@app.get("/")
async def root():
    return {
        "message": "Badminton Analysis Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Export manager for use in other modules
def get_connection_manager():
    return manager

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
