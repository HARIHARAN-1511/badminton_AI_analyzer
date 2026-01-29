import React, { useState, useEffect, useCallback } from 'react';
import './MistakeViewer.css';

const MistakeViewer = ({ mistakes, sessionId }) => {
    const [selectedMistake, setSelectedMistake] = useState(null); // For popup modal
    const [filter, setFilter] = useState('all');

    // Handle keyboard navigation in modal
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (!selectedMistake) return;

            if (e.key === 'Escape') {
                setSelectedMistake(null);
            } else if (e.key === 'ArrowLeft') {
                navigateMistake(-1);
            } else if (e.key === 'ArrowRight') {
                navigateMistake(1);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [selectedMistake, mistakes]);

    // Navigate to previous/next mistake
    const navigateMistake = useCallback((direction) => {
        if (!selectedMistake || !mistakes) return;
        const currentIndex = mistakes.findIndex(m =>
            (m.mistake_id || m.description) === (selectedMistake.mistake_id || selectedMistake.description)
        );
        if (currentIndex === -1) return;

        const newIndex = currentIndex + direction;
        if (newIndex >= 0 && newIndex < mistakes.length) {
            setSelectedMistake(mistakes[newIndex]);
        }
    }, [selectedMistake, mistakes]);

    if (!mistakes || mistakes.length === 0) {
        return (
            <div className="mistake-viewer">
                <div className="mistake-viewer-empty">
                    <span className="empty-icon">✅</span>
                    <h3>No Mistakes Detected</h3>
                    <p>Great performance! No significant mistakes found in this match.</p>
                </div>
            </div>
        );
    }

    const filteredMistakes = mistakes.filter(mistake => {
        if (filter === 'all') return true;
        if (filter === 'player_a') return mistake.player?.includes('A');
        if (filter === 'player_b') return mistake.player?.includes('B');
        if (filter === 'unforced') return mistake.category === 'unforced';
        if (filter === 'tactical') return mistake.category === 'tactical';
        if (filter === 'forced') return mistake.category === 'forced';
        return true;
    });

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'major': return '#ef4444';
            case 'moderate': return '#f97316';
            case 'minor': return '#fbbf24';
            default: return '#888';
        }
    };

    const getCategoryIcon = (category) => {
        switch (category) {
            case 'unforced': return '⚠️';
            case 'forced': return '💪';
            case 'tactical': return '🎯';
            case 'execution': return '🎾';
            default: return '❌';
        }
    };

    const getSeverityLabel = (severity) => {
        switch (severity) {
            case 'major': return { label: 'Major', icon: '🔴' };
            case 'moderate': return { label: 'Moderate', icon: '🟠' };
            case 'minor': return { label: 'Minor', icon: '🟡' };
            default: return { label: 'Unknown', icon: '⚪' };
        }
    };

    // Open modal popup with mistake details
    const openMistakeModal = (mistake, e) => {
        e.stopPropagation();
        setSelectedMistake(mistake);
    };

    // Close modal
    const closeModal = () => {
        setSelectedMistake(null);
    };

    const currentMistakeIndex = selectedMistake
        ? mistakes.findIndex(m => (m.mistake_id || m.description) === (selectedMistake.mistake_id || selectedMistake.description))
        : -1;
    const canGoPrev = currentMistakeIndex > 0;
    const canGoNext = currentMistakeIndex < mistakes.length - 1;

    return (
        <div className="mistake-viewer">
            <div className="mistake-viewer-header">
                <h2>⚠️ Mistake Analysis</h2>
                <div className="mistake-stats">
                    <span className="stat-badge total">{mistakes.length} Total</span>
                    <span className="stat-badge player-a">
                        {mistakes.filter(m => m.player?.includes('A')).length} Player A
                    </span>
                    <span className="stat-badge player-b">
                        {mistakes.filter(m => m.player?.includes('B')).length} Player B
                    </span>
                </div>
            </div>

            <div className="filter-group">
                <label>Filter by:</label>
                <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                    <option value="all">All Mistakes</option>
                    <option value="player_a">Player A</option>
                    <option value="player_b">Player B</option>
                    <option value="unforced">Unforced Errors</option>
                    <option value="tactical">Tactical Errors</option>
                    <option value="forced">Forced Errors</option>
                </select>
            </div>

            {/* Category Legend */}
            <div className="category-legend">
                <div className="legend-item">
                    <span className="legend-icon">⚠️</span>
                    <span>Unforced - Self-inflicted errors</span>
                </div>
                <div className="legend-item">
                    <span className="legend-icon">💪</span>
                    <span>Forced - Opponent outplayed</span>
                </div>
                <div className="legend-item">
                    <span className="legend-icon">🎯</span>
                    <span>Tactical - Poor decision-making</span>
                </div>
            </div>

            <div className="mistakes-list">
                {filteredMistakes.map((mistake, index) => (
                    <div
                        key={mistake.mistake_id || index}
                        className="mistake-card"
                        style={{ borderLeftColor: getSeverityColor(mistake.severity) }}
                        onClick={(e) => openMistakeModal(mistake, e)}
                    >
                        <div className="mistake-header">
                            <div className="mistake-title">
                                <span className="mistake-icon">{getCategoryIcon(mistake.category)}</span>
                                <span className="mistake-type">
                                    {mistake.mistake_type?.replace(/_/g, ' ')}
                                </span>
                            </div>
                            <div className="mistake-meta">
                                <span className="mistake-player">{mistake.player}</span>
                                <span className="mistake-time">{mistake.time?.toFixed(1)}s</span>
                            </div>
                        </div>

                        <p className="mistake-description">{mistake.description}</p>

                        <div className="mistake-card-footer">
                            <span className="rally-badge">Rally {mistake.rally_number}</span>
                            <div className="view-details-btn">
                                👁️ View Details
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {filteredMistakes.length === 0 && (
                <div className="no-results">
                    <p>No mistakes match the current filter.</p>
                    <button onClick={() => setFilter('all')}>Show All Mistakes</button>
                </div>
            )}

            {/* MISTAKE DETAIL POPUP MODAL */}
            {selectedMistake && (
                <div className="mistake-modal-overlay" onClick={closeModal}>
                    <div className="mistake-modal" onClick={(e) => e.stopPropagation()}>
                        {/* Modal Header */}
                        <div className="mistake-modal-header">
                            <h2>
                                <span className="modal-icon">{getCategoryIcon(selectedMistake.category)}</span>
                                {selectedMistake.mistake_type?.replace(/_/g, ' ')}
                            </h2>
                            <div className="modal-header-info">
                                <span className="modal-player-badge">
                                    👤 {selectedMistake.player}
                                </span>
                                <span
                                    className="modal-severity-badge"
                                    style={{ background: getSeverityColor(selectedMistake.severity) }}
                                >
                                    {getSeverityLabel(selectedMistake.severity).icon} {getSeverityLabel(selectedMistake.severity).label}
                                </span>
                            </div>
                            <button className="modal-close-btn" onClick={closeModal} title="Close (Esc)">
                                ✕
                            </button>
                        </div>

                        {/* Modal Content */}
                        <div className="mistake-modal-content">
                            {/* Mistake Info Grid */}
                            <div className="modal-info-grid">
                                <div className="modal-info-card">
                                    <span className="info-icon">🏸</span>
                                    <span className="info-label">Rally</span>
                                    <span className="info-value">{selectedMistake.rally_number || 'N/A'}</span>
                                </div>
                                <div className="modal-info-card">
                                    <span className="info-icon">⏱</span>
                                    <span className="info-label">Time</span>
                                    <span className="info-value">{selectedMistake.time?.toFixed(1)}s</span>
                                </div>
                                <div className="modal-info-card">
                                    <span className="info-icon">🎾</span>
                                    <span className="info-label">Shot Type</span>
                                    <span className="info-value">{selectedMistake.shot_type?.replace(/_/g, ' ') || 'N/A'}</span>
                                </div>
                                <div className="modal-info-card">
                                    <span className="info-icon">📋</span>
                                    <span className="info-label">Category</span>
                                    <span className={`info-value category-${selectedMistake.category}`}>
                                        {selectedMistake.category || 'N/A'}
                                    </span>
                                </div>
                            </div>

                            {/* What Happened Section */}
                            <div className="modal-section">
                                <h4 className="modal-section-title">
                                    <span className="section-icon">📋</span> What Happened
                                </h4>
                                <div className="modal-narrative">
                                    <p>{selectedMistake.description}</p>
                                </div>
                            </div>

                            {/* Explanation Section */}
                            {selectedMistake.explanation && (
                                <div className="modal-section">
                                    <h4 className="modal-section-title">
                                        <span className="section-icon">🔍</span> Detailed Analysis
                                    </h4>
                                    <div className="modal-analysis">
                                        <p>{selectedMistake.explanation}</p>
                                    </div>
                                </div>
                            )}

                            {/* Improvement Suggestion Section */}
                            {selectedMistake.improvement_suggestion && (
                                <div className="modal-section">
                                    <h4 className="modal-section-title">
                                        <span className="section-icon">💡</span> How to Improve
                                    </h4>
                                    <div className="modal-improvement">
                                        <p>{selectedMistake.improvement_suggestion}</p>
                                    </div>
                                </div>
                            )}

                            {/* GIF Clip Section - Auto-loops */}
                            <div className="modal-section">
                                <h4 className="modal-section-title">
                                    <span className="section-icon">🎬</span> Mistake Clip
                                </h4>
                                <div className="modal-clip-container">
                                    <img
                                        src={`/api/analyze/${sessionId}/mistake/${selectedMistake.mistake_id}/clip`}
                                        alt={`Mistake: ${selectedMistake.description}`}
                                        className="modal-mistake-gif"
                                        onError={(e) => {
                                            e.target.style.display = 'none';
                                            e.target.nextSibling.style.display = 'flex';
                                        }}
                                    />
                                    <div className="modal-clip-placeholder" style={{ display: 'none' }}>
                                        <span className="placeholder-icon">🎬</span>
                                        <p>Clip not available for this mistake.</p>
                                        <p className="placeholder-hint">Re-run analysis to generate clips.</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Modal Footer with Navigation */}
                        <div className="mistake-modal-footer">
                            <div className="modal-nav-buttons">
                                <button
                                    className="modal-nav-btn"
                                    onClick={() => navigateMistake(-1)}
                                    disabled={!canGoPrev}
                                    title="Previous Mistake (←)"
                                >
                                    ← Previous
                                </button>
                                <button
                                    className="modal-nav-btn"
                                    onClick={() => navigateMistake(1)}
                                    disabled={!canGoNext}
                                    title="Next Mistake (→)"
                                >
                                    Next →
                                </button>
                            </div>
                            <span className="modal-counter">
                                Mistake {currentMistakeIndex + 1} of {mistakes.length}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MistakeViewer;

