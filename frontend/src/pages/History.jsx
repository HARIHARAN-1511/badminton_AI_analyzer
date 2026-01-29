import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import './History.css';

const History = ({ onSessionLoad }) => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');
    const [sortOrder, setSortOrder] = useState('newest'); // 'newest' or 'oldest'
    const [stats, setStats] = useState(null);
    const [selectedSession, setSelectedSession] = useState(null);
    const [deleteConfirm, setDeleteConfirm] = useState(null);
    const navigate = useNavigate();

    // Sort sessions based on sortOrder
    const sortedSessions = useMemo(() => {
        return [...sessions].sort((a, b) => {
            const dateA = new Date(a.created_at || 0);
            const dateB = new Date(b.created_at || 0);
            return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
        });
    }, [sessions, sortOrder]);

    // Fetch history on mount
    useEffect(() => {
        fetchHistory();
        fetchStats();
    }, [filter]);

    const fetchHistory = async () => {
        try {
            setLoading(true);
            const statusFilter = filter !== 'all' ? `&status=${filter}` : '';
            const response = await fetch(`${API_BASE_URL}/api/history?limit=50${statusFilter}`);
            const data = await response.json();

            if (data.success) {
                setSessions(data.sessions);
            } else {
                setError('Failed to load history');
            }
        } catch (err) {
            setError('Failed to connect to server');
            console.error('Error fetching history:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/history/stats/summary`);
            const data = await response.json();
            if (data.success) {
                setStats(data.stats);
            }
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    };

    const scanLegacySessions = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/history/scan', {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                alert(`Imported ${data.imported} sessions, skipped ${data.skipped} existing`);
                fetchHistory();
                fetchStats();
            }
        } catch (err) {
            alert('Failed to scan for sessions');
        }
    };

    const loadSession = async (session) => {
        try {
            // Fetch full session details and results
            const response = await fetch(`http://localhost:8000/api/history/${session.session_id}`);
            const data = await response.json();

            if (data.success && data.results) {
                // Pass session data to parent for viewing
                if (onSessionLoad) {
                    onSessionLoad({
                        session_id: session.session_id,
                        filename: session.video_filename,
                        video_info: data.results?.video_info
                    }, data.results);
                }
                // Navigate to analysis page
                navigate('/analysis');
            } else {
                alert('Results not available for this session');
            }
        } catch (err) {
            console.error('Error loading session:', err);
            alert('Failed to load session');
        }
    };

    const deleteSession = async (sessionId, deleteFiles = false) => {
        try {
            const response = await fetch(
                `http://localhost:8000/api/history/${sessionId}?delete_files=${deleteFiles}`,
                { method: 'DELETE' }
            );
            const data = await response.json();

            if (data.success) {
                setSessions(prev => prev.filter(s => s.session_id !== sessionId));
                setDeleteConfirm(null);
                fetchStats();
            }
        } catch (err) {
            alert('Failed to delete session');
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const formatDuration = (seconds) => {
        if (!seconds) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'completed':
                return <span className="status-badge completed">✅ Completed</span>;
            case 'processing':
                return <span className="status-badge processing">⏳ Processing</span>;
            case 'failed':
                return <span className="status-badge failed">❌ Failed</span>;
            default:
                return <span className="status-badge">{status}</span>;
        }
    };

    return (
        <div className="history-page">
            <div className="history-header">
                <div className="header-content">
                    <h1>📂 Analysis History</h1>
                    <p>View and manage your past match analyses</p>
                </div>
                <div className="header-actions">
                    <button className="scan-btn" onClick={scanLegacySessions}>
                        🔍 Scan for Sessions
                    </button>
                    <button className="refresh-btn" onClick={fetchHistory}>
                        🔄 Refresh
                    </button>
                </div>
            </div>

            {/* Stats Summary */}
            {stats && (
                <div className="stats-summary">
                    <div className="stat-card total">
                        <span className="stat-icon">📊</span>
                        <span className="stat-value">{stats.total_sessions}</span>
                        <span className="stat-label">Total Sessions</span>
                    </div>
                    <div className="stat-card completed">
                        <span className="stat-icon">✅</span>
                        <span className="stat-value">{stats.completed}</span>
                        <span className="stat-label">Completed</span>
                    </div>
                    <div className="stat-card processing">
                        <span className="stat-icon">⏳</span>
                        <span className="stat-value">{stats.processing}</span>
                        <span className="stat-label">Processing</span>
                    </div>
                    <div className="stat-card failed">
                        <span className="stat-icon">❌</span>
                        <span className="stat-value">{stats.failed}</span>
                        <span className="stat-label">Failed</span>
                    </div>
                </div>
            )}

            {/* Filter Controls */}
            <div className="filter-controls">
                {/* Status Filter Tabs */}
                <div className="filter-tabs">
                    <button
                        className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
                        onClick={() => setFilter('all')}
                    >
                        All Sessions
                    </button>
                    <button
                        className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
                        onClick={() => setFilter('completed')}
                    >
                        Completed
                    </button>
                    <button
                        className={`filter-tab ${filter === 'processing' ? 'active' : ''}`}
                        onClick={() => setFilter('processing')}
                    >
                        Processing
                    </button>
                    <button
                        className={`filter-tab ${filter === 'failed' ? 'active' : ''}`}
                        onClick={() => setFilter('failed')}
                    >
                        Failed
                    </button>
                </div>

                {/* Sort Order Toggle */}
                <div className="sort-controls">
                    <span className="sort-label">Sort by:</span>
                    <button
                        className={`sort-btn ${sortOrder === 'newest' ? 'active' : ''}`}
                        onClick={() => setSortOrder('newest')}
                    >
                        📅 Newest First
                    </button>
                    <button
                        className={`sort-btn ${sortOrder === 'oldest' ? 'active' : ''}`}
                        onClick={() => setSortOrder('oldest')}
                    >
                        📆 Oldest First
                    </button>
                </div>
            </div>

            {/* Sessions List */}
            <div className="sessions-container">
                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading history...</p>
                    </div>
                ) : error ? (
                    <div className="error-state">
                        <span className="error-icon">⚠️</span>
                        <h3>Error Loading History</h3>
                        <p>{error}</p>
                        <button onClick={fetchHistory}>Try Again</button>
                    </div>
                ) : sessions.length === 0 ? (
                    <div className="empty-state">
                        <span className="empty-icon">📭</span>
                        <h3>No Analysis History</h3>
                        <p>Upload and analyze a match video to see it here.</p>
                        <button onClick={() => navigate('/')}>
                            📤 Upload Video
                        </button>
                    </div>
                ) : (
                    <div className="sessions-grid">
                        {sortedSessions.map((session) => (
                            <div
                                key={session.session_id}
                                className={`session-card ${session.status}`}
                            >
                                <div className="session-header">
                                    <div className="session-info">
                                        <h3 className="video-name">
                                            🎬 {session.video_filename || 'Unknown Video'}
                                        </h3>
                                        {getStatusBadge(session.status)}
                                    </div>
                                    <button
                                        className="delete-btn"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setDeleteConfirm(session.session_id);
                                        }}
                                        title="Delete session"
                                    >
                                        🗑️
                                    </button>
                                </div>

                                <div className="session-meta">
                                    <div className="meta-row">
                                        <span className="meta-label">📅 Created:</span>
                                        <span className="meta-value">{formatDate(session.created_at)}</span>
                                    </div>
                                    {session.status === 'completed' && (
                                        <>
                                            <div className="meta-row">
                                                <span className="meta-label">🏸 Rallies:</span>
                                                <span className="meta-value">{session.rallies_count || 0}</span>
                                            </div>
                                            <div className="meta-row">
                                                <span className="meta-label">⚠️ Mistakes:</span>
                                                <span className="meta-value">{session.mistakes_count || 0}</span>
                                            </div>
                                            <div className="meta-row">
                                                <span className="meta-label">⏱ Duration:</span>
                                                <span className="meta-value">{formatDuration(session.total_duration)}</span>
                                            </div>
                                            {session.winner && (
                                                <div className="meta-row">
                                                    <span className="meta-label">🏆 Winner:</span>
                                                    <span className="meta-value winner">{session.winner}</span>
                                                </div>
                                            )}
                                        </>
                                    )}
                                    {session.status === 'processing' && (
                                        <div className="progress-bar-container">
                                            <div
                                                className="progress-bar"
                                                style={{ width: `${session.progress || 0}%` }}
                                            ></div>
                                            <span className="progress-text">{Math.round(session.progress || 0)}%</span>
                                        </div>
                                    )}
                                    {session.status === 'failed' && session.error_message && (
                                        <div className="error-message">
                                            {session.error_message}
                                        </div>
                                    )}
                                </div>

                                <div className="session-players">
                                    <span className="player player-a">{session.player_a_name || 'Player A'}</span>
                                    <span className="vs">vs</span>
                                    <span className="player player-b">{session.player_b_name || 'Player B'}</span>
                                </div>

                                {session.status === 'completed' && (
                                    <button
                                        className="view-results-btn"
                                        onClick={() => loadSession(session)}
                                    >
                                        👁️ View Results
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Delete Confirmation Modal */}
            {deleteConfirm && (
                <div className="delete-modal-overlay" onClick={() => setDeleteConfirm(null)}>
                    <div className="delete-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>🗑️ Delete Session?</h3>
                        <p>Are you sure you want to delete this analysis session?</p>
                        <div className="delete-options">
                            <button
                                className="delete-history-only"
                                onClick={() => deleteSession(deleteConfirm, false)}
                            >
                                Remove from History
                            </button>
                            <button
                                className="delete-all"
                                onClick={() => deleteSession(deleteConfirm, true)}
                            >
                                Delete All Files
                            </button>
                        </div>
                        <button
                            className="cancel-btn"
                            onClick={() => setDeleteConfirm(null)}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default History;
