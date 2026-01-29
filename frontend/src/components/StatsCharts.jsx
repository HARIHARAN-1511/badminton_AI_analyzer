import React, { useState } from 'react'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell,
    LineChart, Line,
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    AreaChart, Area
} from 'recharts'
import './StatsCharts.css'

const PLAYER_A_COLOR = '#FF7F27'
const PLAYER_B_COLOR = '#A29BFE' // Matching existing purple-ish theme
const COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6']

function StatsCharts({ statistics, sessionId }) {
    const [activeTab, setActiveTab] = useState('match') // 'match', 'playerA', 'playerB'

    const matchSummary = statistics.match_summary || {}
    const rallyDurations = statistics.rally_durations || []
    const shotDist = statistics.shot_distribution || {}
    const shotByPlayer = statistics.shot_distribution_by_player || {}
    const winLoss = statistics.win_loss_breakdown || {}
    const errorAnalysis = statistics.error_analysis || {}
    const playerComparison = statistics.player_comparison || {}
    const rallyLengthStats = statistics.rally_length_stats || {}
    const momentum = statistics.momentum_analysis || {}

    const renderTabs = () => (
        <div className="stats-tabs">
            <button
                className={`stats-tab ${activeTab === 'match' ? 'active' : ''}`}
                onClick={() => setActiveTab('match')}
            >
                Match Overview
            </button>
            <button
                className={`stats-tab ${activeTab === 'playerA' ? 'active' : ''}`}
                onClick={() => setActiveTab('playerA')}
            >
                Player A Performance
            </button>
            <button
                className={`stats-tab ${activeTab === 'playerB' ? 'active' : ''}`}
                onClick={() => setActiveTab('playerB')}
            >
                Player B Performance
            </button>
        </div>
    )

    const renderMatchStats = () => (
        <>
            {/* Rally Duration Chart */}
            <div className="chart-container">
                <div className="chart-header">
                    <h3 className="chart-title">Rally Duration Analysis</h3>
                    <p className="chart-explanation">
                        Displays the length of each rally in seconds. Spikes indicate long-drawn battles that test endurance, while short bars represent quick points or errors.
                    </p>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={rallyDurations.slice(0, 20)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                        <XAxis
                            dataKey="rally_number"
                            stroke="#a0a0b0"
                            tick={{ fill: '#a0a0b0' }}
                        />
                        <YAxis
                            stroke="#a0a0b0"
                            tick={{ fill: '#a0a0b0' }}
                            label={{ value: 'Duration (s)', angle: -90, position: 'insideLeft', fill: '#a0a0b0' }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1a1a24',
                                border: '1px solid #2a2a3a',
                                borderRadius: '8px'
                            }}
                        />
                        <Bar
                            dataKey="duration"
                            fill="#3498db"
                            radius={[4, 4, 0, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            <div className="charts-row">
                {/* Shot Distribution Pie */}
                <div className="chart-container half">
                    <div className="chart-header">
                        <h3 className="chart-title">Match Shot Mix</h3>
                        <p className="chart-explanation">
                            The overall proportion of shot types used by both players. Ideal for understanding the general pace and style of the match.
                        </p>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={Object.entries(shotDist.counts || {}).map(([name, value]) => ({ name, value }))}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={100}
                                paddingAngle={2}
                                dataKey="value"
                                label={({ name, percent }) => `${name.replace(/_/g, ' ')} ${(percent * 100).toFixed(0)}%`}
                                labelLine={{ stroke: '#a0a0b0' }}
                            >
                                {Object.entries(shotDist.counts || {}).map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1a1a24',
                                    border: '1px solid #2a2a3a',
                                    borderRadius: '8px'
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Win/Loss Pie */}
                <div className="chart-container half">
                    <div className="chart-header">
                        <h3 className="chart-title">Rally Wins Split</h3>
                        <p className="chart-explanation">
                            A direct comparison of total rallies won by each player. This shows who dominated the scoring throughout the session.
                        </p>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={[
                                    { name: 'Player A', value: winLoss.player_a_wins || 0 },
                                    { name: 'Player B', value: winLoss.player_b_wins || 0 }
                                ]}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={100}
                                paddingAngle={5}
                                dataKey="value"
                                label={({ name, value }) => `${name}: ${value}`}
                            >
                                <Cell fill={PLAYER_A_COLOR} />
                                <Cell fill={PLAYER_B_COLOR} />
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1a1a24',
                                    border: '1px solid #2a2a3a',
                                    borderRadius: '8px'
                                }}
                            />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Match Momentum */}
            <div className="chart-container">
                <div className="chart-header">
                    <h3 className="chart-title">Match Momentum</h3>
                    <p className="chart-explanation">
                        Visualizes point streaks. Bars going up indicate Player A is pulling ahead, while bars going down show Player B taking the lead in momentum.
                    </p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={momentum.data || []}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                        <XAxis
                            dataKey="rally"
                            stroke="#a0a0b0"
                            tick={{ fill: '#a0a0b0' }}
                            label={{ value: 'Rally', position: 'insideBottom', offset: -5, fill: '#a0a0b0' }}
                        />
                        <YAxis
                            stroke="#a0a0b0"
                            tick={{ fill: '#a0a0b0' }}
                            label={{ value: 'Score Diff', angle: -90, position: 'insideLeft', fill: '#a0a0b0' }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1a1a24',
                                border: '1px solid #2a2a3a',
                                borderRadius: '8px'
                            }}
                            formatter={(value) => [value, 'Score Diff (A-B)']}
                        />
                        <defs>
                            <linearGradient id="momentumGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3498db" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#3498db" stopOpacity={0.1} />
                            </linearGradient>
                        </defs>
                        <Area
                            type="monotone"
                            dataKey="diff"
                            stroke="#3498db"
                            fill="url(#momentumGradient)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
                <p className="chart-note">
                    Positive values = Player A leading, Negative = Player B leading
                </p>
            </div>

            {/* Rally Length Distribution */}
            <div className="chart-container">
                <div className="chart-header">
                    <h3 className="chart-title">Match Intensity Stats</h3>
                    <p className="chart-explanation">
                        Aggregated shot counts per rally. A high average suggest technical rallies, while a high max shows the peak stamina required in the match.
                    </p>
                </div>
                <div className="stats-summary">
                    <div className="stat-item">
                        <span className="stat-label">Min Shots</span>
                        <span className="stat-value">{rallyLengthStats.min || 0}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Max Shots</span>
                        <span className="stat-value">{rallyLengthStats.max || 0}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Average</span>
                        <span className="stat-value">{rallyLengthStats.average || 0}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Median</span>
                        <span className="stat-value">{rallyLengthStats.median || 0}</span>
                    </div>
                </div>
            </div>
        </>
    )

    const renderPlayerStats = (player) => {
        const isA = player === 'playerA'
        const playerColor = isA ? PLAYER_A_COLOR : PLAYER_B_COLOR
        const playerData = isA ? shotByPlayer.player_a : shotByPlayer.player_b
        const playerErrors = isA ? errorAnalysis.player_a : errorAnalysis.player_b
        const playerSkills = isA ? playerComparison.player_a : playerComparison.player_b
        const name = isA ? 'Player A' : 'Player B'

        return (
            <>
                <div className="charts-row">
                    {/* Player Shot Distribution */}
                    <div className="chart-container half">
                        <div className="chart-header">
                            <h3 className="chart-title">{name} Shot Selection</h3>
                            <p className="chart-explanation">
                                Break down of what shots {name} uses most. Frequent smashes reveal an aggressive player, while clears and drops suggest a more tactical approach.
                            </p>
                        </div>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={Object.entries(playerData || {}).map(([name, value]) => ({ name, value }))}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={2}
                                    dataKey="value"
                                    label={({ name, percent }) => `${name.replace(/_/g, ' ')} ${(percent * 100).toFixed(0)}%`}
                                >
                                    {Object.entries(playerData || {}).map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1a1a24',
                                        border: '1px solid #2a2a3a',
                                        borderRadius: '8px'
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Player Skill Radar */}
                    <div className="chart-container half">
                        <div className="chart-header">
                            <h3 className="chart-title">{name} Skill Profile</h3>
                            <p className="chart-explanation">
                                A comprehensive evaluation of {name}'s game. This radar chart measures performance across five key badminton pillars.
                            </p>
                        </div>
                        <ResponsiveContainer width="100%" height={300}>
                            <RadarChart
                                data={[
                                    { metric: 'Attack', value: playerSkills?.attack || 50 },
                                    { metric: 'Defense', value: playerSkills?.defense || 50 },
                                    { metric: 'Net Play', value: playerSkills?.net_play || 50 },
                                    { metric: 'Power', value: playerSkills?.power || 50 },
                                    { metric: 'Consistency', value: playerSkills?.consistency || 50 }
                                ]}
                            >
                                <PolarGrid stroke="#2a2a3a" />
                                <PolarAngleAxis dataKey="metric" stroke="#a0a0b0" tick={{ fill: '#a0a0b0' }} />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#2a2a3a" />
                                <Radar
                                    name={name}
                                    dataKey="value"
                                    stroke={playerColor}
                                    fill={playerColor}
                                    fillOpacity={0.4}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1a1a24',
                                        border: '1px solid #2a2a3a',
                                        borderRadius: '8px'
                                    }}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Error Analysis */}
                <div className="chart-container">
                    <div className="chart-header">
                        <h3 className="chart-title">{name} Error Breakdown</h3>
                        <p className="chart-explanation">
                            Analyzes where {name} lost points. Higher "Net" or "Out" bars indicate where technical practice is needed to improve precision.
                        </p>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart
                            data={[
                                { type: 'Net Errors', count: playerErrors?.net || 0 },
                                { type: 'Out Errors', count: playerErrors?.out || 0 },
                                { type: 'Tactical Errors', count: playerErrors?.tactical || 0 }
                            ]}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                            <XAxis dataKey="type" stroke="#a0a0b0" tick={{ fill: '#a0a0b0' }} />
                            <YAxis stroke="#a0a0b0" tick={{ fill: '#a0a0b0' }} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1a1a24',
                                    border: '1px solid #2a2a3a',
                                    borderRadius: '8px'
                                }}
                            />
                            <Bar dataKey="count" name="Errors" fill={playerColor} radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </>
        )
    }

    return (
        <div className="stats-charts">
            {renderTabs()}
            <div className="stats-content">
                {activeTab === 'match' && renderMatchStats()}
                {activeTab === 'playerA' && renderPlayerStats('playerA')}
                {activeTab === 'playerB' && renderPlayerStats('playerB')}
            </div>
        </div>
    )
}

export default StatsCharts

