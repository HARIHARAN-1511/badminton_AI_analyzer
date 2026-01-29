import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import ThemeToggle from './components/ThemeToggle'
import Home from './pages/Home'
import Analysis from './pages/Analysis'
import Report from './pages/Report'
import History from './pages/History'
import axios from 'axios'
import { API_BASE_URL } from './config'
import './App.css'

axios.defaults.baseURL = API_BASE_URL;

function App() {
    const [sessionData, setSessionData] = useState(null)
    const [analysisResults, setAnalysisResults] = useState(null)

    // Handler for loading a session from history
    const handleSessionLoad = (session, results) => {
        setSessionData(session)
        setAnalysisResults(results)
    }

    return (
        <ThemeProvider>
            <Router>
                <div className="app">
                    <header className="app-header">
                        <div className="container">
                            <div className="header-content">
                                <div className="header-left">
                                    <ThemeToggle />
                                    <a href="/" className="logo">
                                        <span className="logo-icon">🏸</span>
                                        <span className="logo-text">Badminton Analysis</span>
                                    </a>
                                </div>
                                <nav className="nav">
                                    <a href="/" className="nav-link">Home</a>
                                    <a href="/history" className="nav-link">History</a>
                                </nav>
                            </div>
                        </div>
                    </header>

                    <main className="app-main">
                        <Routes>
                            <Route
                                path="/"
                                element={
                                    <Home
                                        onSessionCreated={setSessionData}
                                        sessionData={sessionData}
                                    />
                                }
                            />
                            <Route
                                path="/analysis"
                                element={
                                    <Analysis
                                        sessionData={sessionData}
                                        onAnalysisComplete={setAnalysisResults}
                                        analysisResults={analysisResults}
                                    />
                                }
                            />
                            <Route
                                path="/report"
                                element={
                                    <Report
                                        sessionData={sessionData}
                                        analysisResults={analysisResults}
                                    />
                                }
                            />
                            <Route
                                path="/history"
                                element={
                                    <History
                                        onSessionLoad={handleSessionLoad}
                                    />
                                }
                            />
                        </Routes>
                    </main>

                    <footer className="app-footer">
                        <div className="container">
                            <p>Badminton Analysis Platform - AI-Powered Match Analysis</p>
                        </div>
                    </footer>
                </div>
            </Router>
        </ThemeProvider>
    )
}

export default App
