import React from 'react'
import { useNavigate } from 'react-router-dom'
import VideoUpload from '../components/VideoUpload'
import './Home.css'

function Home({ onSessionCreated, sessionData }) {
    const navigate = useNavigate()

    const handleUploadComplete = (data) => {
        onSessionCreated(data)
    }

    const handleStartAnalysis = () => {
        navigate('/analysis')
    }

    return (
        <div className="home-page">
            <div className="container">
                {/* Hero Section */}
                <section className="hero">
                    <div className="hero-content">
                        <h1 className="hero-title">
                            AI-Powered Badminton
                            <span className="hero-highlight"> Match Analysis</span>
                        </h1>
                        <p className="hero-subtitle">
                            Upload your match video and get comprehensive analysis with rally segmentation,
                            mistake detection, performance insights, and detailed PDF reports.
                        </p>
                    </div>

                    <div className="hero-features">
                        <div className="feature-card">
                            <div className="feature-icon">🎯</div>
                            <h3>Rally Detection</h3>
                            <p>Automatically segments video into individual rallies</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">📊</div>
                            <h3>Shot Analysis</h3>
                            <p>Classifies 18 different shot types with probabilities</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">⚠️</div>
                            <h3>Mistake Detection</h3>
                            <p>Identifies errors with improvement suggestions</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">📈</div>
                            <h3>Statistics</h3>
                            <p>Comprehensive graphs and player comparisons</p>
                        </div>
                    </div>
                </section>

                {/* Upload Section */}
                <section className="upload-section">
                    <h2 className="section-title text-center">Upload Your Match Video</h2>
                    <p className="section-subtitle text-center">
                        Supports MP4 format up to 2GB. Analysis takes approximately 1-2 minutes per minute of video.
                    </p>

                    <VideoUpload onUploadComplete={handleUploadComplete} />

                    {sessionData && (
                        <div className="upload-success fade-in">
                            <div className="success-card">
                                <div className="success-icon">✓</div>
                                <div className="success-content">
                                    <h3>Video Uploaded Successfully!</h3>
                                    <p className="success-details">
                                        <strong>File:</strong> {sessionData.filename}<br />
                                        <strong>Duration:</strong> {sessionData.video_info?.duration_formatted || 'Unknown'}<br />
                                        <strong>Resolution:</strong> {sessionData.video_info?.width}x{sessionData.video_info?.height}
                                    </p>
                                    <button
                                        className="btn btn-primary btn-lg"
                                        onClick={handleStartAnalysis}
                                    >
                                        Start Analysis →
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </section>

                {/* How It Works */}
                <section className="how-it-works">
                    <h2 className="section-title text-center">How It Works</h2>
                    <div className="steps">
                        <div className="step">
                            <div className="step-number">1</div>
                            <h3>Upload Video</h3>
                            <p>Upload your badminton match video in MP4 format</p>
                        </div>
                        <div className="step-arrow">→</div>
                        <div className="step">
                            <div className="step-number">2</div>
                            <h3>AI Analysis</h3>
                            <p>Our AI tracks the shuttle, detects rallies, and classifies shots</p>
                        </div>
                        <div className="step-arrow">→</div>
                        <div className="step">
                            <div className="step-number">3</div>
                            <h3>View Results</h3>
                            <p>Browse rallies, view mistakes, and explore statistics</p>
                        </div>
                        <div className="step-arrow">→</div>
                        <div className="step">
                            <div className="step-number">4</div>
                            <h3>Download Report</h3>
                            <p>Get a comprehensive PDF report with all analysis</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    )
}

export default Home
