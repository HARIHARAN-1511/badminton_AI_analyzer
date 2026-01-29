"""
Database module for storing analysis session history.
Uses SQLite for lightweight, persistent storage.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "history.db")

def init_database():
    """Initialize the database and create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                video_filename TEXT,
                player_a_name TEXT DEFAULT 'Player A',
                player_b_name TEXT DEFAULT 'Player B',
                status TEXT DEFAULT 'pending',
                progress REAL DEFAULT 0,
                rallies_count INTEGER DEFAULT 0,
                mistakes_count INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0,
                winner TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                thumbnail_path TEXT,
                video_path TEXT,
                error_message TEXT
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id ON sessions(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON sessions(created_at DESC)
        """)
        
        conn.commit()
        print(f"Database initialized at: {DB_PATH}")

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_session(session_id: str, video_filename: str, video_path: str, 
                   player_a: str = "Player A", player_b: str = "Player B") -> int:
    """Create a new analysis session record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, video_filename, video_path, player_a_name, player_b_name, status)
            VALUES (?, ?, ?, ?, ?, 'processing')
        """, (session_id, video_filename, video_path, player_a, player_b))
        conn.commit()
        return cursor.lastrowid

def update_session_progress(session_id: str, progress: float, status: str = None, 
                            current_step: str = None):
    """Update session progress during analysis."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("""
                UPDATE sessions SET progress = ?, status = ? WHERE session_id = ?
            """, (progress, status, session_id))
        else:
            cursor.execute("""
                UPDATE sessions SET progress = ? WHERE session_id = ?
            """, (progress, session_id))
        conn.commit()

def complete_session(session_id: str, rallies_count: int, mistakes_count: int, 
                     total_duration: float, winner: str = None, thumbnail_path: str = None):
    """Mark a session as completed with results summary."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET status = 'completed', 
                progress = 100,
                rallies_count = ?,
                mistakes_count = ?,
                total_duration = ?,
                winner = ?,
                thumbnail_path = ?,
                completed_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (rallies_count, mistakes_count, total_duration, winner, thumbnail_path, session_id))
        conn.commit()

def fail_session(session_id: str, error_message: str):
    """Mark a session as failed with error message."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET status = 'failed', 
                error_message = ?,
                completed_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (error_message, session_id))
        conn.commit()

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific session by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_all_sessions(limit: int = 50, offset: int = 0, 
                     status_filter: str = None) -> List[Dict[str, Any]]:
    """Get all sessions with optional filtering."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM sessions"
        params = []
        
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_session_count(status_filter: str = None) -> int:
    """Get total count of sessions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = ?", (status_filter,))
        else:
            cursor.execute("SELECT COUNT(*) FROM sessions")
        
        return cursor.fetchone()[0]

def delete_session(session_id: str) -> bool:
    """Delete a session from history."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount > 0

def session_exists(session_id: str) -> bool:
    """Check if a session already exists."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
        return cursor.fetchone() is not None

# Initialize database on module import
init_database()
