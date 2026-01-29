import React, { useState } from 'react';
import './PlayerComparison.css';

const PlayerComparison = ({ comparison, weaknesses, playerA, playerB }) => {
    const [activeTab, setActiveTab] = useState('overview');

    if (!comparison) {
        return (
            <div className="player-comparison">
                <div className="comparison-empty">
                    <span className="empty-icon">⚔️</span>
                    <h3>Player Comparison</h3>
                    <p>Analysis data will appear here after processing.</p>
                </div>
            </div>
        );
    }

    const playerAData = comparison.player_a || {};
    const playerBData = comparison.player_b || {};
    const playerAWeakness = weaknesses?.player_a || {};
    const playerBWeakness = weaknesses?.player_b || {};

    const getScoreColor = (score) => {
        if (score >= 70) return '#22c55e';
        if (score >= 50) return '#fbbf24';
        return '#ef4444';
    };

    return (
        <div className="player-comparison">
            <div className="comparison-header">
                <h2>⚔️ Player Comparison</h2>
                <div className="tab-buttons">
                    <button
                        className={activeTab === 'overview' ? 'active' : ''}
                        onClick={() => setActiveTab('overview')}
                    >
                        Overview
                    </button>
                    <button
                        className={activeTab === 'weaknesses' ? 'active' : ''}
                        onClick={() => setActiveTab('weaknesses')}
                    >
                        Weaknesses
                    </button>
                    <button
                        className={activeTab === 'improvements' ? 'active' : ''}
                        onClick={() => setActiveTab('improvements')}
                    >
                        Improvements
                    </button>
                </div>
            </div>

            {/* Player Name Headers */}
            <div className="players-header">
                <div className="player-header player-a">
                    <div className="player-icon">A</div>
                    <h3>{playerAData.name || playerA || 'Player A'}</h3>
                </div>
                <div className="vs-badge">VS</div>
                <div className="player-header player-b">
                    <div className="player-icon">B</div>
                    <h3>{playerBData.name || playerB || 'Player B'}</h3>
                </div>
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
                <div className="tab-content overview-tab">
                    {/* Score Cards */}
                    <div className="score-cards">
                        <div className="score-card player-a">
                            <div
                                className="score-circle"
                                style={{ borderColor: getScoreColor(playerAData.average_score || 50) }}
                            >
                                <span className="score-value">{Math.round(playerAData.average_score || 50)}</span>
                            </div>
                            <span className="score-label">Avg Score</span>
                        </div>
                        <div className="score-card player-b">
                            <div
                                className="score-circle"
                                style={{ borderColor: getScoreColor(playerBData.average_score || 50) }}
                            >
                                <span className="score-value">{Math.round(playerBData.average_score || 50)}</span>
                            </div>
                            <span className="score-label">Avg Score</span>
                        </div>
                    </div>

                    {/* Stats Comparison */}
                    <div className="stats-comparison">
                        <div className="stat-row">
                            <span className="stat-value-a">{playerAData.rallies_won || 0}</span>
                            <span className="stat-label">Rallies Won</span>
                            <span className="stat-value-b">{playerBData.rallies_won || 0}</span>
                        </div>
                        <div className="stat-bar">
                            <div
                                className="bar-fill player-a"
                                style={{
                                    width: `${(playerAData.rallies_won || 0) / Math.max((playerAData.rallies_won || 0) + (playerBData.rallies_won || 0), 1) * 100}%`
                                }}
                            />
                            <div
                                className="bar-fill player-b"
                                style={{
                                    width: `${(playerBData.rallies_won || 0) / Math.max((playerAData.rallies_won || 0) + (playerBData.rallies_won || 0), 1) * 100}%`
                                }}
                            />
                        </div>

                        <div className="stat-row">
                            <span className="stat-value-a">{playerAData.total_shots || 0}</span>
                            <span className="stat-label">Total Shots</span>
                            <span className="stat-value-b">{playerBData.total_shots || 0}</span>
                        </div>
                        <div className="stat-bar">
                            <div
                                className="bar-fill player-a"
                                style={{
                                    width: `${(playerAData.total_shots || 0) / Math.max((playerAData.total_shots || 0) + (playerBData.total_shots || 0), 1) * 100}%`
                                }}
                            />
                            <div
                                className="bar-fill player-b"
                                style={{
                                    width: `${(playerBData.total_shots || 0) / Math.max((playerAData.total_shots || 0) + (playerBData.total_shots || 0), 1) * 100}%`
                                }}
                            />
                        </div>

                        <div className="stat-row">
                            <span className="stat-value-a error">{playerAData.total_mistakes || 0}</span>
                            <span className="stat-label">Mistakes</span>
                            <span className="stat-value-b error">{playerBData.total_mistakes || 0}</span>
                        </div>
                        <div className="stat-bar reverse">
                            <div
                                className="bar-fill error-a"
                                style={{
                                    width: `${(playerAData.total_mistakes || 0) / Math.max((playerAData.total_mistakes || 0) + (playerBData.total_mistakes || 0), 1) * 100}%`
                                }}
                            />
                            <div
                                className="bar-fill error-b"
                                style={{
                                    width: `${(playerBData.total_mistakes || 0) / Math.max((playerAData.total_mistakes || 0) + (playerBData.total_mistakes || 0), 1) * 100}%`
                                }}
                            />
                        </div>
                    </div>

                    {/* Total Rallies */}
                    <div className="total-rallies">
                        <span className="total-label">Total Rallies Analyzed:</span>
                        <span className="total-value">{comparison.total_rallies || 0}</span>
                    </div>
                </div>
            )}

            {/* Weaknesses Tab */}
            {activeTab === 'weaknesses' && (
                <div className="tab-content weaknesses-tab">
                    <div className="weaknesses-grid">
                        <div className="weakness-column player-a">
                            <h4>{playerAData.name || 'Player A'} Weaknesses</h4>
                            {playerAWeakness.weaknesses && playerAWeakness.weaknesses.length > 0 ? (
                                <ul className="weakness-list">
                                    {playerAWeakness.weaknesses.map((weakness, i) => (
                                        <li key={i} className={`weakness-item ${weakness.severity}`}>
                                            <span className="weakness-type">{weakness.type}</span>
                                            <span className="weakness-count">{weakness.count}x</span>
                                            <span className="weakness-desc">{weakness.description}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="no-weaknesses">No significant weaknesses detected</p>
                            )}

                            {playerAWeakness.summary && (
                                <div className="weakness-summary">
                                    <p>{playerAWeakness.summary}</p>
                                </div>
                            )}
                        </div>

                        <div className="weakness-column player-b">
                            <h4>{playerBData.name || 'Player B'} Weaknesses</h4>
                            {playerBWeakness.weaknesses && playerBWeakness.weaknesses.length > 0 ? (
                                <ul className="weakness-list">
                                    {playerBWeakness.weaknesses.map((weakness, i) => (
                                        <li key={i} className={`weakness-item ${weakness.severity}`}>
                                            <span className="weakness-type">{weakness.type}</span>
                                            <span className="weakness-count">{weakness.count}x</span>
                                            <span className="weakness-desc">{weakness.description}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="no-weaknesses">No significant weaknesses detected</p>
                            )}

                            {playerBWeakness.summary && (
                                <div className="weakness-summary">
                                    <p>{playerBWeakness.summary}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Improvements Tab */}
            {activeTab === 'improvements' && (
                <div className="tab-content improvements-tab">
                    <div className="improvements-grid">
                        <div className="improvement-column player-a">
                            <h4>💡 Suggestions for {playerAData.name || 'Player A'}</h4>
                            {playerAWeakness.improvements && playerAWeakness.improvements.length > 0 ? (
                                <ul className="improvement-list">
                                    {playerAWeakness.improvements.map((improvement, i) => (
                                        <li key={i} className="improvement-item">
                                            <span className="improvement-icon">✓</span>
                                            <span className="improvement-text">{improvement}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="no-improvements">Keep up the good work!</p>
                            )}
                        </div>

                        <div className="improvement-column player-b">
                            <h4>💡 Suggestions for {playerBData.name || 'Player B'}</h4>
                            {playerBWeakness.improvements && playerBWeakness.improvements.length > 0 ? (
                                <ul className="improvement-list">
                                    {playerBWeakness.improvements.map((improvement, i) => (
                                        <li key={i} className="improvement-item">
                                            <span className="improvement-icon">✓</span>
                                            <span className="improvement-text">{improvement}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="no-improvements">Keep up the good work!</p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PlayerComparison;
