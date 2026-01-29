# 🏸 Badminton Match Analysis Platform

AI-powered badminton match video analysis platform that provides comprehensive rally segmentation, mistake detection, performance analytics, and detailed PDF reports.

![Platform Overview](https://img.shields.io/badge/Platform-Web%20Application-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎯 Rally Detection
- Automatic segmentation of match video into individual rallies
- Ball tracking using computer vision
- Hit point detection with trajectory analysis

### 🏸 Shot Classification
- Classifies 18 different shot types:
  - Serves (short, long)
  - Net shots (net shot, return net, cross-court)
  - Attack shots (smash, wrist smash, rush, drop)
  - Defense shots (lob, defensive lob, defensive drive)
  - Drives (drive, driven flight, back-court drive)
  - And more...

### ⚠️ Mistake Detection
- Identifies player errors (net errors, out-of-bounds, tactical errors)
- Provides detailed explanations for each mistake
- Generates personalized improvement suggestions
- Extracts video clips of mistake moments

### 📊 Comprehensive Statistics
- Rally duration analysis
- Shot type distribution
- Player comparison radar charts
- Landing position heatmaps
- Match momentum graphs
- Error analysis breakdowns

### 📄 PDF Reports
- Professional match analysis reports
- Embedded charts and visualizations
- Rally-by-rally breakdown
- Personalized training recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn

### Installation

1. **Clone the repository:**
```bash
cd CoachAI-Projects-main/BadmintonAnalysisPlatform
```

2. **Set up the backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Set up the frontend:**
```bash
cd ../frontend

# Install dependencies
npm install
```

### Running the Application

1. **Start the backend server:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the frontend dev server (in a new terminal):**
```bash
cd frontend
npm run dev
```

3. **Open your browser:**
Navigate to `http://localhost:3000`

## 📁 Project Structure

```
BadmintonAnalysisPlatform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/
│   │   │   ├── upload.py        # Video upload endpoints
│   │   │   ├── analysis.py      # Analysis endpoints
│   │   │   └── reports.py       # PDF generation
│   │   ├── core/
│   │   │   ├── video_processor.py    # Video handling
│   │   │   ├── rally_segmentation.py # Rally detection
│   │   │   ├── shot_classifier.py    # Shot classification
│   │   │   ├── mistake_analyzer.py   # Error detection
│   │   │   └── statistics.py         # Stats generation
│   │   └── utils/
│   │       └── pdf_generator.py      # PDF reports
│   ├── data/
│   │   ├── uploads/             # Uploaded videos
│   │   └── output/              # Analysis results
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoUpload.jsx
│   │   │   ├── RallyBrowser.jsx
│   │   │   ├── MistakeViewer.jsx
│   │   │   └── StatsCharts.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Analysis.jsx
│   │   │   └── Report.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
│
└── README.md
```

## 🎮 Usage Guide

### 1. Upload Your Video
- Navigate to the home page
- Drag and drop your badminton match video (MP4 format)
- Click "Upload Video"

### 2. Start Analysis
- After upload, click "Start Analysis"
- Watch real-time progress as the AI processes:
  - Video frame extraction
  - Ball tracking
  - Rally boundary detection
  - Shot classification
  - Mistake detection
  - Statistics calculation

### 3. Explore Results
- **Rallies Tab**: Browse individual rallies with shot sequences
- **Mistakes Tab**: View player errors and improvement suggestions
- **Statistics Tab**: Interactive charts and player comparisons

### 4. Generate Report
- Click "View Full Report" to preview
- Generate and download comprehensive PDF report

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload video file |
| `/api/analyze` | POST | Start analysis |
| `/api/analyze/{id}/status` | GET | Get analysis progress |
| `/api/analyze/{id}/results` | GET | Get complete results |
| `/api/analyze/{id}/rallies` | GET | Get rally list |
| `/api/analyze/{id}/mistakes` | GET | Get all mistakes |
| `/api/report/{id}/generate` | POST | Generate PDF |
| `/api/report/{id}/download` | GET | Download PDF |
| `/ws/{session_id}` | WebSocket | Real-time progress |

## 🧠 AI Components

### Ball Tracking
CPU-optimized shuttlecock detection using:
- Background subtraction
- Color-based detection (white shuttlecock)
- Motion prediction for trajectory continuity

### Rally Segmentation
Adapted from CoachAI's segmentation algorithm:
- Velocity vector analysis
- Direction change detection for hit points
- Rally end detection (ball at rest)

### Shot Classification
18-class classification based on:
- Shot trajectory (start/landing position)
- Court zone analysis (front/mid/back court)
- Previous shot context

## ⚙️ Configuration

### Backend Settings
Edit `backend/app/core/rally_segmentation.py` for:
- Court coordinate calibration
- Detection sensitivity thresholds
- Rally duration limits

### Analysis Performance
The system is optimized for CPU-only processing:
- Frame skipping for faster analysis
- Batch processing
- Background subtraction optimization

## 🐛 Troubleshooting

### "Analysis taking too long"
- Long videos (>30 min) may take 30+ minutes
- Consider trimming video to specific sets

### "No rallies detected"
- Ensure video has clear court view
- Check that camera angle is top-down or broadcast angle
- Video quality should be at least 720p

### "Ball tracking issues"
- Lighting should be consistent
- Shuttlecock should be visible against background
- Court lines should be clearly visible

## 📝 License

This project is part of CoachAI and is licensed under the MIT License.

## 🙏 Acknowledgments

- CoachAI Project for the foundational algorithms
- ShuttleSet dataset for shot type taxonomy
- TrackNet for ball tracking inspiration

---

Made with ❤️ for badminton enthusiasts
