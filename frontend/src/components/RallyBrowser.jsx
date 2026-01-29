import React, { useState, useEffect, useCallback } from 'react';
import './RallyBrowser.css';

const RallyBrowser = ({ rallies, sessionId, onRallySelect }) => {
    const [selectedRally, setSelectedRally] = useState(null);
    const [modalRally, setModalRally] = useState(null); // For popup modal
    const [modalTab, setModalTab] = useState('overview'); // 'overview', 'mistakes', 'shots', 'video'
    const [filter, setFilter] = useState('all');
    const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

    // Get current rally index for navigation
    const getCurrentRallyIndex = useCallback(() => {
        if (!modalRally || !rallies) return -1;
        return rallies.findIndex(r => r.rally_number === modalRally.rally_number);
    }, [modalRally, rallies]);

    // Navigate to previous/next rally in modal
    const navigateRally = useCallback((direction) => {
        const currentIndex = getCurrentRallyIndex();
        if (currentIndex === -1) return;

        const newIndex = currentIndex + direction;
        if (newIndex >= 0 && newIndex < rallies.length) {
            setModalRally(rallies[newIndex]);
            setModalTab('overview'); // Reset to overview tab when navigating
        }
    }, [getCurrentRallyIndex, rallies]);

    // Handle keyboard navigation in modal
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (!modalRally) return;

            if (e.key === 'Escape') {
                setModalRally(null);
            } else if (e.key === 'ArrowLeft') {
                navigateRally(-1);
            } else if (e.key === 'ArrowRight') {
                navigateRally(1);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [modalRally, navigateRally]);

    if (!rallies || rallies.length === 0) {
        return (
            <div className="rally-browser">
                <div className="rally-browser-empty">
                    <span className="empty-icon">🏸</span>
                    <h3>No Rallies Found</h3>
                    <p>Upload and analyze a match video to see rallies here.</p>
                </div>
            </div>
        );
    }

    const filteredRallies = rallies.filter(rally => {
        if (filter === 'all') return true;
        if (filter === 'player_a') return rally.winner?.includes('A');
        if (filter === 'player_b') return rally.winner?.includes('B');
        if (filter === 'errors') return rally.end_reason === 'net' || rally.end_reason === 'out';
        if (filter === 'long') return rally.duration > 15;
        return true;
    });

    const handleRallyClick = (rally) => {
        setSelectedRally(rally.rally_number);
        if (onRallySelect) {
            onRallySelect(rally);
        }
    };

    // Open modal popup with rally details
    const openRallyModal = (rally, e) => {
        e.stopPropagation();
        setModalRally(rally);
        setModalTab('overview');
    };

    // Close modal
    const closeModal = () => {
        setModalRally(null);
    };

    const formatDuration = (seconds) => {
        if (!seconds) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const getEndReasonIcon = (reason) => {
        switch (reason) {
            case 'net': return '🌐';
            case 'out': return '⬅️';
            case 'in_court': return '✅';
            default: return '🏸';
        }
    };

    const getEndReasonLabel = (reason) => {
        switch (reason) {
            case 'net': return 'Net Error';
            case 'out': return 'Out of Bounds';
            case 'in_court': return 'Winner';
            default: return 'Point';
        }
    };

    // Render modal tab content
    const renderModalTabContent = () => {
        if (!modalRally) return null;

        switch (modalTab) {
            case 'overview':
                return (
                    <>
                        {/* Rally Stats Grid */}
                        <div className="modal-section">
                            <h4 className="modal-section-title">
                                <span className="section-icon">📊</span> Rally Statistics
                            </h4>
                            <div className="modal-stats-grid">
                                <div className="modal-stat-card">
                                    <div className="modal-stat-value">{formatDuration(modalRally.duration)}</div>
                                    <div className="modal-stat-label">Duration</div>
                                </div>
                                <div className="modal-stat-card">
                                    <div className="modal-stat-value">{modalRally.shots?.length || modalRally.total_shots || 0}</div>
                                    <div className="modal-stat-label">Total Shots</div>
                                </div>
                                <div className="modal-stat-card">
                                    <div className="modal-stat-value">{modalRally.mistakes?.length || 0}</div>
                                    <div className="modal-stat-label">Mistakes</div>
                                </div>
                                <div className="modal-stat-card">
                                    <div className="modal-stat-value">{getEndReasonLabel(modalRally.end_reason)}</div>
                                    <div className="modal-stat-label">End Reason</div>
                                </div>
                            </div>
                        </div>

                        {/* Narrative Description */}
                        {modalRally.narrative && (
                            <div className="modal-section">
                                <h4 className="modal-section-title">
                                    <span className="section-icon">📝</span> Rally Description
                                </h4>
                                <div className="modal-narrative">
                                    <p dangerouslySetInnerHTML={{
                                        __html: modalRally.narrative
                                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                            .replace(/\n/g, '<br/>')
                                    }} />
                                </div>
                            </div>
                        )}

                        {/* Key Moments */}
                        {modalRally.key_moments && modalRally.key_moments.length > 0 && (
                            <div className="modal-section">
                                <h4 className="modal-section-title">
                                    <span className="section-icon">⭐</span> Key Moments
                                </h4>
                                <ul className="key-moments-list">
                                    {modalRally.key_moments.slice(0, 5).map((moment, i) => (
                                        <li key={i} className={`moment ${moment.type}`}>
                                            <span className="moment-time">{moment.time?.toFixed(1)}s</span>
                                            <span className="moment-desc">{moment.description}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Player Comparison */}
                        {modalRally.player_comparison && (
                            <div className="modal-section">
                                <h4 className="modal-section-title">
                                    <span className="section-icon">⚔️</span> Player Comparison
                                </h4>
                                <div className="modal-comparison">
                                    <div className="modal-player-card player-a">
                                        <h5 className="modal-player-name">
                                            {modalRally.player_comparison.player_a?.name || 'Player A'}
                                        </h5>
                                        <div className="modal-player-stats">
                                            <div className="modal-player-stat">
                                                <span className="stat-name">Shots Played</span>
                                                <span className="stat-value">{modalRally.player_comparison.player_a?.shots_played || 0}</span>
                                            </div>
                                            <div className="modal-player-stat">
                                                <span className="stat-name">Mistakes</span>
                                                <span className="stat-value">{modalRally.player_comparison.player_a?.mistakes_count || 0}</span>
                                            </div>
                                            <div className="modal-player-stat">
                                                <span className="stat-name">Performance</span>
                                                <span className="stat-value">{modalRally.player_comparison.player_a?.performance_score || 0}%</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="modal-vs-divider">VS</div>
                                    <div className="modal-player-card player-b">
                                        <h5 className="modal-player-name">
                                            {modalRally.player_comparison.player_b?.name || 'Player B'}
                                        </h5>
                                        <div className="modal-player-stats">
                                            <div className="modal-player-stat">
                                                <span className="stat-name">Shots Played</span>
                                                <span className="stat-value">{modalRally.player_comparison.player_b?.shots_played || 0}</span>
                                            </div>
                                            <div className="modal-player-stat">
                                                <span className="stat-name">Mistakes</span>
                                                <span className="stat-value">{modalRally.player_comparison.player_b?.mistakes_count || 0}</span>
                                            </div>
                                            <div className="modal-player-stat">
                                                <span className="stat-name">Performance</span>
                                                <span className="stat-value">{modalRally.player_comparison.player_b?.performance_score || 0}%</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                {modalRally.player_comparison.comparison_summary && (
                                    <p className="comparison-summary">{modalRally.player_comparison.comparison_summary}</p>
                                )}
                            </div>
                        )}

                        {/* Tactical Analysis */}
                        {modalRally.tactical_analysis && (
                            <div className="modal-section">
                                <h4 className="modal-section-title">
                                    <span className="section-icon">🎯</span> Tactical Analysis
                                </h4>
                                <div className="tactical-section">
                                    <p>{modalRally.tactical_analysis}</p>
                                </div>
                            </div>
                        )}
                    </>
                );

            case 'mistakes':
                return (
                    <div className="modal-section">
                        <h4 className="modal-section-title">
                            <span className="section-icon">⚠️</span> Mistakes Detected
                        </h4>
                        {modalRally.mistakes && modalRally.mistakes.length > 0 ? (
                            <div className="modal-mistakes-list">
                                {modalRally.mistakes.map((mistake, i) => (
                                    <div key={i} className={`modal-mistake-card ${mistake.severity || 'minor'}`}>
                                        <div className="modal-mistake-header">
                                            <span className={`modal-mistake-type ${mistake.severity || 'minor'}`}>
                                                {mistake.severity === 'major' ? '🔴' : '🟡'} {mistake.mistake_type?.replace(/_/g, ' ')}
                                            </span>
                                            <span className="modal-mistake-player">{mistake.player}</span>
                                        </div>
                                        <p className="modal-mistake-desc">{mistake.description}</p>
                                        <p className="modal-mistake-explanation">{mistake.explanation}</p>
                                        {mistake.improvement_suggestion && (
                                            <div className="modal-mistake-suggestion">
                                                <span className="suggestion-icon">💡</span>
                                                <span>{mistake.improvement_suggestion}</span>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="modal-video-placeholder">
                                <span className="placeholder-icon">✅</span>
                                <p>No mistakes detected in this rally.</p>
                            </div>
                        )}
                    </div>
                );

            case 'shots':
                return (
                    <div className="modal-section">
                        <h4 className="modal-section-title">
                            <span className="section-icon">🏸</span> Shot Sequence
                        </h4>
                        {modalRally.shots && modalRally.shots.length > 0 ? (
                            <div className="modal-shot-timeline">
                                {modalRally.shots.map((shot, i) => (
                                    <div key={i} className={`modal-shot-item ${shot.player?.includes('A') ? 'player-a' : 'player-b'}`}>
                                        <div className="modal-shot-header">
                                            <span className="modal-shot-number">Shot {shot.shot_number}</span>
                                            <span className="modal-shot-type">{shot.shot_type?.replace(/_/g, ' ')}</span>
                                        </div>
                                        <span className="modal-shot-player">{shot.player}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="modal-video-placeholder">
                                <span className="placeholder-icon">🏸</span>
                                <p>No shot data available for this rally.</p>
                            </div>
                        )}
                    </div>
                );



            default:
                return null;
        }
    };

    const currentRallyIndex = modalRally ? rallies.findIndex(r => r.rally_number === modalRally.rally_number) : -1;
    const canGoPrev = currentRallyIndex > 0;
    const canGoNext = currentRallyIndex < rallies.length - 1;

    return (
        <div className="rally-browser">
            <div className="rally-browser-header">
                <h2>Rally Browser</h2>
                <div className="rally-controls">
                    <div className="filter-group">
                        <label>Filter:</label>
                        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                            <option value="all">All Rallies ({rallies.length})</option>
                            <option value="player_a">Player A Wins</option>
                            <option value="player_b">Player B Wins</option>
                            <option value="errors">Errors Only</option>
                            <option value="long">Long Rallies (&gt;15s)</option>
                        </select>
                    </div>
                    <div className="view-toggle">
                        <button
                            className={viewMode === 'grid' ? 'active' : ''}
                            onClick={() => setViewMode('grid')}
                            title="Grid View"
                        >
                            ▦
                        </button>
                        <button
                            className={viewMode === 'list' ? 'active' : ''}
                            onClick={() => setViewMode('list')}
                            title="List View"
                        >
                            ≡
                        </button>
                    </div>
                </div>
            </div>

            <div className="rally-stats-bar">
                <div className="stat">
                    <span className="stat-value">{rallies.length}</span>
                    <span className="stat-label">Total Rallies</span>
                </div>
                <div className="stat">
                    <span className="stat-value">
                        {rallies.filter(r => r.winner?.includes('A')).length}
                    </span>
                    <span className="stat-label">Player A Wins</span>
                </div>
                <div className="stat">
                    <span className="stat-value">
                        {rallies.filter(r => r.winner?.includes('B')).length}
                    </span>
                    <span className="stat-label">Player B Wins</span>
                </div>
                <div className="stat">
                    <span className="stat-value">
                        {Math.round(rallies.reduce((sum, r) => sum + (r.duration || 0), 0) / rallies.length)}s
                    </span>
                    <span className="stat-label">Avg Duration</span>
                </div>
            </div>

            <div className={`rally-list ${viewMode}`}>
                {filteredRallies.map((rally) => (
                    <div
                        key={rally.rally_number}
                        className={`rally-card ${selectedRally === rally.rally_number ? 'selected' : ''}`}
                        onClick={() => handleRallyClick(rally)}
                    >
                        <div className="rally-card-header">
                            <div className="rally-number">
                                Rally {rally.rally_number}
                            </div>
                            <div className="rally-duration">
                                <span className="duration-icon">⏱</span>
                                {formatDuration(rally.duration)}
                            </div>
                        </div>

                        <div className="rally-card-body">
                            <div className="rally-winner">
                                <span className={`winner-badge ${rally.winner?.includes('A') ? 'player-a' : 'player-b'}`}>
                                    {rally.winner || 'Unknown'}
                                </span>
                            </div>

                            <div className="rally-details">
                                <div className="detail-item">
                                    <span className="detail-icon">🏸</span>
                                    <span>{rally.shots?.length || rally.total_shots || 0} shots</span>
                                </div>
                                <div className="detail-item">
                                    <span className="detail-icon">{getEndReasonIcon(rally.end_reason)}</span>
                                    <span>{getEndReasonLabel(rally.end_reason)}</span>
                                </div>
                            </div>

                            {rally.mistakes && rally.mistakes.length > 0 && (
                                <div className="rally-mistakes-badge">
                                    ⚠️ {rally.mistakes.length} mistake{rally.mistakes.length > 1 ? 's' : ''}
                                </div>
                            )}
                        </div>

                        <button
                            className="expand-btn"
                            onClick={(e) => openRallyModal(rally, e)}
                            title="View Details"
                        >
                            👁️
                        </button>
                    </div>
                ))}
            </div>

            {filteredRallies.length === 0 && (
                <div className="no-results">
                    <p>No rallies match the current filter.</p>
                    <button onClick={() => setFilter('all')}>Show All Rallies</button>
                </div>
            )}

            {/* ENHANCED POPUP MODAL WITH TABS */}
            {modalRally && (
                <div className="rally-modal-overlay" onClick={closeModal}>
                    <div className="rally-modal" onClick={(e) => e.stopPropagation()}>
                        {/* Modal Header */}
                        <div className="rally-modal-header">
                            <h2>
                                <span className="rally-icon">🏸</span>
                                Rally {modalRally.rally_number}
                            </h2>
                            <div className="modal-header-info">
                                <span className="modal-duration">
                                    ⏱ {formatDuration(modalRally.duration)}
                                </span>
                                <span className={`modal-winner-badge ${modalRally.winner?.includes('A') ? 'player-a' : 'player-b'}`}>
                                    🏆 {modalRally.winner || 'Unknown'}
                                </span>
                            </div>
                            <button className="modal-close-btn" onClick={closeModal} title="Close (Esc)">
                                ✕
                            </button>
                        </div>

                        {/* Modal Tabs */}
                        <div className="rally-modal-tabs">
                            <button
                                className={`modal-tab ${modalTab === 'overview' ? 'active' : ''}`}
                                onClick={() => setModalTab('overview')}
                            >
                                <span className="tab-icon">📊</span> Overview
                            </button>
                            <button
                                className={`modal-tab ${modalTab === 'mistakes' ? 'active' : ''}`}
                                onClick={() => setModalTab('mistakes')}
                            >
                                <span className="tab-icon">⚠️</span> Mistakes
                                {modalRally.mistakes?.length > 0 && (
                                    <span style={{
                                        marginLeft: 6,
                                        background: '#ef4444',
                                        color: 'white',
                                        borderRadius: 10,
                                        padding: '2px 8px',
                                        fontSize: '0.75rem'
                                    }}>
                                        {modalRally.mistakes.length}
                                    </span>
                                )}
                            </button>
                            <button
                                className={`modal-tab ${modalTab === 'shots' ? 'active' : ''}`}
                                onClick={() => setModalTab('shots')}
                            >
                                <span className="tab-icon">🏸</span> Shot Sequence
                            </button>

                        </div>

                        {/* Modal Content */}
                        <div className="rally-modal-content">
                            {renderModalTabContent()}
                        </div>

                        {/* Modal Footer with Navigation */}
                        <div className="rally-modal-footer">
                            <div className="modal-nav-buttons">
                                <button
                                    className="modal-nav-btn"
                                    onClick={() => navigateRally(-1)}
                                    disabled={!canGoPrev}
                                    title="Previous Rally (←)"
                                >
                                    ← Previous
                                </button>
                                <button
                                    className="modal-nav-btn"
                                    onClick={() => navigateRally(1)}
                                    disabled={!canGoNext}
                                    title="Next Rally (→)"
                                >
                                    Next →
                                </button>
                            </div>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                Rally {currentRallyIndex + 1} of {rallies.length}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RallyBrowser;
