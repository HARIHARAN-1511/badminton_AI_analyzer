import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import './Report.css'

function Report({ sessionData, analysisResults }) {
    const navigate = useNavigate()
    const [generating, setGenerating] = useState(false)
    const [pdfReady, setPdfReady] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!sessionData || !analysisResults) {
            navigate('/')
        }
    }, [sessionData, analysisResults, navigate])

    const generateReport = async () => {
        if (!sessionData?.session_id) return

        setGenerating(true)
        setError(null)

        try {
            await axios.post(`/api/report/${sessionData.session_id}/generate`)
            setPdfReady(true)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to generate report')
        } finally {
            setGenerating(false)
        }
    }

    const downloadReport = () => {
        window.open(`${API_BASE_URL}/api/report/${sessionData.session_id}/download`, '_blank')
    }

    if (!sessionData || !analysisResults) {
        return null
    }

    const stats = analysisResults.statistics || {}
    const matchSummary = stats.match_summary || {}

    return (
        <div className="report-page">
            <div className="container">
                <h1 className="page-title">Match Analysis Report</h1>
                <p className="page-subtitle">
                    Comprehensive analysis of {analysisResults.player_a || 'Player A'} vs {analysisResults.player_b || 'Player B'}
                </p>

                {/* Report Preview */}
                <div className="report-preview">
                    {/* Match Summary Section */}
                    <section className="report-section">
                        <h2 className="report-section-title">📊 Match Summary</h2>
                        <div className="summary-grid">
                            <div className="summary-item">
                                <span className="summary-label">Total Rallies</span>
                                <span className="summary-value">{matchSummary.total_rallies || 0}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">{analysisResults.player_a || 'Player A'} Wins</span>
                                <span className="summary-value player-a">{matchSummary.player_a_wins || 0}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">{analysisResults.player_b || 'Player B'} Wins</span>
                                <span className="summary-value player-b">{matchSummary.player_b_wins || 0}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Avg Rally Duration</span>
                                <span className="summary-value">{matchSummary.average_rally_duration || 0}s</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Total Shots</span>
                                <span className="summary-value">{matchSummary.total_shots || 0}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Mistakes Detected</span>
                                <span className="summary-value">{analysisResults.total_mistakes || 0}</span>
                            </div>
                        </div>
                    </section>

                    {/* Rally Overview */}
                    <section className="report-section">
                        <h2 className="report-section-title">🏸 Rally Overview</h2>
                        <div className="rally-timeline">
                            {(analysisResults.rallies || []).slice(0, 10).map((rally, idx) => (
                                <div key={idx} className="rally-item">
                                    <span className="rally-number">R{rally.rally_number || idx + 1}</span>
                                    <span className="rally-duration">{rally.duration?.toFixed(1)}s</span>
                                    <span className={`rally-winner ${rally.winner?.includes('A') ? 'player-a' : 'player-b'}`}>
                                        {rally.winner || 'Unknown'}
                                    </span>
                                    <span className="rally-shots">{(rally.shots || []).length} shots</span>
                                </div>
                            ))}
                            {(analysisResults.rallies || []).length > 10 && (
                                <div className="rally-more">
                                    +{analysisResults.rallies.length - 10} more rallies
                                </div>
                            )}
                        </div>
                    </section>

                    {/* Mistake Summary */}
                    <section className="report-section">
                        <h2 className="report-section-title">⚠️ Mistake Summary</h2>
                        {analysisResults.total_mistakes > 0 ? (
                            <div className="mistake-summary">
                                <div className="mistake-player">
                                    <h4 className="player-a">{analysisResults.player_a || 'Player A'}</h4>
                                    <ul>
                                        {(analysisResults.rallies || [])
                                            .flatMap(r => r.mistakes || [])
                                            .filter(m => m.player?.includes('A'))
                                            .slice(0, 3)
                                            .map((m, idx) => (
                                                <li key={idx}>{m.description}</li>
                                            ))}
                                    </ul>
                                </div>
                                <div className="mistake-player">
                                    <h4 className="player-b">{analysisResults.player_b || 'Player B'}</h4>
                                    <ul>
                                        {(analysisResults.rallies || [])
                                            .flatMap(r => r.mistakes || [])
                                            .filter(m => m.player?.includes('B'))
                                            .slice(0, 3)
                                            .map((m, idx) => (
                                                <li key={idx}>{m.description}</li>
                                            ))}
                                    </ul>
                                </div>
                            </div>
                        ) : (
                            <p>No significant mistakes detected.</p>
                        )}
                    </section>

                    {/* What's in the PDF */}
                    <section className="report-section pdf-contents">
                        <h2 className="report-section-title">📄 Full PDF Report Includes</h2>
                        <ul className="pdf-list">
                            <li>✅ Complete match summary with all statistics</li>
                            <li>✅ Rally-by-rally breakdown with descriptions</li>
                            <li>✅ Detailed player performance analysis</li>
                            <li>✅ Shot distribution charts and graphs</li>
                            <li>✅ Mistake analysis with improvement suggestions</li>
                            <li>✅ Player comparison radar charts</li>
                            <li>✅ Landing position heatmaps</li>
                            <li>✅ Match momentum graph</li>
                            <li>✅ Personalized training recommendations</li>
                        </ul>
                    </section>
                </div>

                {/* Generate/Download Buttons */}
                <div className="report-actions">
                    {error && (
                        <div className="error-message">
                            <span>⚠️</span> {error}
                        </div>
                    )}

                    {!pdfReady ? (
                        <button
                            className="btn btn-primary btn-lg"
                            onClick={generateReport}
                            disabled={generating}
                        >
                            {generating ? (
                                <>
                                    <span className="spinner" style={{ width: 20, height: 20 }}></span>
                                    Generating PDF...
                                </>
                            ) : (
                                '📄 Generate PDF Report'
                            )}
                        </button>
                    ) : (
                        <button
                            className="btn btn-success btn-lg"
                            onClick={downloadReport}
                        >
                            ⬇️ Download PDF Report
                        </button>
                    )}

                    <button
                        className="btn btn-secondary"
                        onClick={() => navigate('/analysis')}
                    >
                        ← Back to Analysis
                    </button>
                </div>
            </div>
        </div>
    )
}

export default Report
