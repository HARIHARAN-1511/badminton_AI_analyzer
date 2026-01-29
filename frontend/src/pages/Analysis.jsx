import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import RallyBrowser from '../components/RallyBrowser'
import MistakeViewer from '../components/MistakeViewer'
import StatsCharts from '../components/StatsCharts'
import PlayerComparison from '../components/PlayerComparison'
import { WS_BASE_URL, API_BASE_URL } from '../config'
import './Analysis.css'

function Analysis({ sessionData, onAnalysisComplete, analysisResults }) {
    const navigate = useNavigate()
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [progress, setProgress] = useState(0)
    const [currentStep, setCurrentStep] = useState('')
    const [error, setError] = useState(null)
    const [activeTab, setActiveTab] = useState('rallies')
    const wsRef = useRef(null)

    // Redirect if no session
    useEffect(() => {
        if (!sessionData) {
            navigate('/')
        }
    }, [sessionData, navigate])

    // Start analysis
    const startAnalysis = async () => {
        if (!sessionData?.session_id) return

        setIsAnalyzing(true)
        setProgress(0)
        setCurrentStep('Initializing AI pipeline...')
        setError(null)

        try {
            // Connect WebSocket for progress updates
            const wsUrl = `${WS_BASE_URL}/ws/${sessionData.session_id}`
            wsRef.current = new WebSocket(wsUrl)

            wsRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data)

                if (data.type === 'progress') {
                    setProgress(data.progress)
                    setCurrentStep(data.step)
                } else if (data.type === 'complete') {
                    setProgress(100)
                    setCurrentStep('Analysis complete!')
                    fetchResults()
                } else if (data.type === 'error') {
                    setError(data.error)
                    setIsAnalyzing(false)
                }
            }

            wsRef.current.onerror = () => {
                console.log('WebSocket error, falling back to polling')
            }

            // Start analysis
            await axios.post('/api/analyze', {
                session_id: sessionData.session_id,
                player_a_name: 'Player A',
                player_b_name: 'Player B'
            })

            // If WebSocket not working, poll for status
            if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
                pollForStatus()
            }

        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to start analysis')
            setIsAnalyzing(false)
        }
    }

    const pollForStatus = async () => {
        const interval = setInterval(async () => {
            try {
                const response = await axios.get(`/api/analyze/${sessionData.session_id}/status`)
                const status = response.data

                setProgress(status.progress || 0)
                setCurrentStep(status.current_step || 'Processing...')

                if (status.status === 'completed') {
                    clearInterval(interval)
                    fetchResults()
                } else if (status.status === 'failed') {
                    clearInterval(interval)
                    setError(status.error || 'Analysis failed')
                    setIsAnalyzing(false)
                }
            } catch (err) {
                console.error('Status check failed:', err)
            }
        }, 2000)
    }

    const fetchResults = async () => {
        try {
            const response = await axios.get(`/api/analyze/${sessionData.session_id}/results`)
            onAnalysisComplete(response.data)
            setIsAnalyzing(false)
        } catch (err) {
            setError('Failed to fetch results')
            setIsAnalyzing(false)
        }
    }

    // Extract all mistakes from rallies
    const getAllMistakes = () => {
        if (!analysisResults?.rallies) return []
        const mistakes = []
        analysisResults.rallies.forEach((rally, index) => {
            if (rally.mistakes) {
                rally.mistakes.forEach(mistake => {
                    mistakes.push({
                        ...mistake,
                        rally_number: index + 1
                    })
                })
            }
        })
        return mistakes
    }

    // Cleanup
    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close()
            }
        }
    }, [])

    if (!sessionData) {
        return null
    }

    return (
        <div className="analysis-page">
            <div className="container">
                <h1 className="page-title">🏸 Match Analysis</h1>

                {/* Analysis Progress */}
                {!analysisResults && (
                    <div className="analysis-start-section">
                        {!isAnalyzing ? (
                            <div className="start-analysis-card">
                                <h2>Ready to Analyze</h2>
                                <p>Video: <strong>{sessionData.filename}</strong></p>
                                <p>Duration: <strong>{sessionData.video_info?.duration_formatted}</strong></p>

                                <div className="analysis-features">
                                    <h3>AI Analysis Features:</h3>
                                    <ul>
                                        <li>🎯 Automatic Rally Detection</li>
                                        <li>🏸 Shot Type Classification</li>
                                        <li>⚠️ Mistake Detection with Video Clips</li>
                                        <li>⚔️ Player Comparison Side-by-Side</li>
                                        <li>📊 Comprehensive Statistics</li>
                                        <li>📝 Detailed Rally Narratives</li>
                                    </ul>
                                </div>

                                {error && (
                                    <div className="error-message">
                                        <span>⚠️</span> {error}
                                    </div>
                                )}

                                <button
                                    className="btn btn-primary btn-lg"
                                    onClick={startAnalysis}
                                >
                                    🚀 Start AI Analysis
                                </button>
                            </div>
                        ) : (
                            <div className="analysis-progress-card">
                                <h2>🔍 Analyzing Your Match</h2>
                                <p className="progress-step">{currentStep}</p>

                                <div className="progress-container">
                                    <div className="progress-bar">
                                        <div
                                            className="progress-bar-fill"
                                            style={{ width: `${progress}%` }}
                                        />
                                    </div>
                                    <span className="progress-percent">{Math.round(progress)}%</span>
                                </div>

                                <div className="progress-stages">
                                    <div className={`stage ${progress >= 5 ? 'active' : ''}`}>
                                        <span className="stage-icon">📚</span>
                                        <span>Training Data</span>
                                    </div>
                                    <div className={`stage ${progress >= 12 ? 'active' : ''}`}>
                                        <span className="stage-icon">📹</span>
                                        <span>Video Processing</span>
                                    </div>
                                    <div className={`stage ${progress >= 35 ? 'active' : ''}`}>
                                        <span className="stage-icon">🎯</span>
                                        <span>Rally Detection</span>
                                    </div>
                                    <div className={`stage ${progress >= 50 ? 'active' : ''}`}>
                                        <span className="stage-icon">🏸</span>
                                        <span>Shot Classification</span>
                                    </div>
                                    <div className={`stage ${progress >= 65 ? 'active' : ''}`}>
                                        <span className="stage-icon">⚠️</span>
                                        <span>Mistakes + Clips</span>
                                    </div>
                                    <div className={`stage ${progress >= 72 ? 'active' : ''}`}>
                                        <span className="stage-icon">📝</span>
                                        <span>Descriptions</span>
                                    </div>
                                    <div className={`stage ${progress >= 80 ? 'active' : ''}`}>
                                        <span className="stage-icon">⚔️</span>
                                        <span>Comparison</span>
                                    </div>
                                    <div className={`stage ${progress >= 90 ? 'active' : ''}`}>
                                        <span className="stage-icon">📊</span>
                                        <span>Statistics</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Analysis Results */}
                {analysisResults && (
                    <>
                        {/* Summary Stats */}
                        <div className="stats-row">
                            <div className="stat-card">
                                <div className="stat-value">{analysisResults.total_rallies || 0}</div>
                                <div className="stat-label">Total Rallies</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{analysisResults.total_mistakes || 0}</div>
                                <div className="stat-label">Mistakes Found</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">
                                    {analysisResults.statistics?.match_summary?.average_shots_per_rally || 0}
                                </div>
                                <div className="stat-label">Avg Shots/Rally</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">
                                    {analysisResults.video_info?.duration_formatted || '0:00'}
                                </div>
                                <div className="stat-label">Match Duration</div>
                            </div>
                            <div className="stat-card winner-card">
                                <div className="stat-value">
                                    {analysisResults.match_comparison?.player_a?.rallies_won >
                                        analysisResults.match_comparison?.player_b?.rallies_won
                                        ? analysisResults.player_a
                                        : analysisResults.player_b}
                                </div>
                                <div className="stat-label">Leading Player</div>
                            </div>
                        </div>

                        {/* Tab Navigation */}
                        <div className="tabs">
                            <button
                                className={`tab ${activeTab === 'rallies' ? 'active' : ''}`}
                                onClick={() => setActiveTab('rallies')}
                            >
                                📋 Rallies
                            </button>
                            <button
                                className={`tab ${activeTab === 'mistakes' ? 'active' : ''}`}
                                onClick={() => setActiveTab('mistakes')}
                            >
                                ⚠️ Mistakes
                            </button>
                            <button
                                className={`tab ${activeTab === 'comparison' ? 'active' : ''}`}
                                onClick={() => setActiveTab('comparison')}
                            >
                                ⚔️ Comparison
                            </button>
                            <button
                                className={`tab ${activeTab === 'stats' ? 'active' : ''}`}
                                onClick={() => setActiveTab('stats')}
                            >
                                📊 Statistics
                            </button>
                        </div>

                        {/* Tab Content */}
                        <div className="tab-content">
                            {activeTab === 'rallies' && (
                                <RallyBrowser
                                    rallies={analysisResults.rallies || []}
                                    sessionId={sessionData.session_id}
                                />
                            )}
                            {activeTab === 'mistakes' && (
                                <MistakeViewer
                                    mistakes={getAllMistakes()}
                                    sessionId={sessionData.session_id}
                                />
                            )}
                            {activeTab === 'comparison' && (
                                <PlayerComparison
                                    comparison={analysisResults.match_comparison}
                                    weaknesses={analysisResults.player_weaknesses}
                                    playerA={analysisResults.player_a}
                                    playerB={analysisResults.player_b}
                                />
                            )}
                            {activeTab === 'stats' && (
                                <StatsCharts
                                    statistics={analysisResults.statistics || {}}
                                    sessionId={sessionData.session_id}
                                />
                            )}
                        </div>

                        {/* Generate Report Button */}
                        <div className="report-section">
                            <button
                                className="btn btn-success btn-lg"
                                onClick={() => navigate('/report')}
                            >
                                📄 Generate Full PDF Report
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}

export default Analysis
