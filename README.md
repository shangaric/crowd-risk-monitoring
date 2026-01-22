# Crowd Risk Monitoring Platform

A live crowd risk monitoring platform that aggregates multiple CCTV camera feeds and continuously analyzes crowd behavior to detect emergent hazards such as stampede risk, congestion, and panic movement.

## System Overview

This platform provides real-time crowd risk assessment through:

- **Multi-camera aggregation**: Process multiple CCTV feeds simultaneously
- **Real-time analysis**: Continuous frame-by-frame crowd behavior analysis
- **Risk detection**: Identifies density surges, motion instability, and directional conflicts
- **Visual dashboard**: Professional control-room interface with heatmaps, graphs, and alerts
- **Decision support**: Human-readable explanations and recommended actions

## Technology Stack

### Core Analytics
- **Python 3.8+**: Core language for all system components
- **OpenCV**: Video ingestion, frame processing, and optical flow calculation
- **NumPy**: High-performance array operations for density, motion, and risk computations
- **Scikit-learn**: Lightweight ML models for smoothing and short-term risk trend prediction

### Backend Services
- **FastAPI**: Modern, fast web framework for REST API and WebSocket endpoints
- **WebSockets**: Real-time bidirectional communication for live data updates
- **Uvicorn**: ASGI server for running FastAPI application

### Dashboard
- **Streamlit**: Rapid development of real-time control-room dashboard
- **Plotly**: Interactive time-series charts and visualizations
- **Pandas**: Data manipulation and analysis

### Storage & Logging
- **Local storage**: Incident history and reporting (JSON-based)
- **Logs**: System activity and error logging

## ML & Analytics Process

### Input
- Multiple live or recorded CCTV video feeds
- Each feed processed frame-by-frame with configurable frame skipping

### Feature Extraction

For each camera frame, the system extracts:

1. **Crowd Density per Region**
   - Uses background subtraction (MOG2)
   - Divides frame into configurable grid (default 4x4)
   - Calculates foreground pixel ratio per region

2. **Motion Intensity**
   - Optical flow calculation using Farneback method
   - Computes magnitude of flow vectors
   - Normalized to 0-1 scale

3. **Directional Conflict**
   - Detects opposing movement vectors
   - Identifies angles differing by ~180 degrees
   - Critical indicator for stampede risk

### Risk Computation

**Local Risk Score per Region:**
- Weighted combination of:
  - Density (40% weight)
  - Motion intensity (30% weight)
  - Directional conflict (30% weight)
- Non-linear scaling (exponential risk for high values)

**Crowd Risk Index (0-1 scale):**
- Aggregates all region risks
- Applies boost factors for critical conditions:
  - High directional conflict → 1.3x multiplier
  - Density surge > 0.6 → 1.2x multiplier

**Explainable Risk Factors:**
- Density surge: Peak density above threshold
- Motion instability: Standard deviation of motion across regions
- Directional conflict: Maximum conflict score across regions
- Average density: Mean density across all regions
- Peak motion: Maximum motion intensity

### Alert Levels
- **Safe**: Risk index < 0.3
- **Moderate**: Risk index 0.3 - 0.8
- **Critical**: Risk index ≥ 0.8

## Dashboard Components

### A. Multi-Camera View Panel
- Displays multiple camera feeds simultaneously
- Each feed labeled with:
  - Camera ID
  - Location
  - Timestamp
  - Current risk index
  - Alert level status

### B. Risk Heatmap Overlay
- Color-coded heatmaps overlaid on each camera feed
- Color scheme:
  - **Green** → Safe (risk < 0.3)
  - **Yellow** → Moderate (risk 0.3 - 0.8)
  - **Red** → Critical (risk ≥ 0.8)
- Grid-based visualization (4x4 regions)

### C. Crowd Risk Index Graph
- Time-series chart showing risk index evolution
- Multiple camera feeds plotted together
- Clearly marks critical and moderate threshold crossings
- Interactive hover details

### D. Alerts Panel
- List of current alerts with:
  - Severity (Warning / Critical)
  - Camera ID
  - Location
  - Risk score
  - Status indicator
  - Timestamp
  - Detected cause

### E. Critical Alert Details Section
When risk is high, displays:
- Camera ID
- Location (e.g., "East Exit Gate")
- Crowd Risk Index value
- Detected cause (e.g., "Density Surge + Directional Conflict")
- Risk factor breakdown
- Recommended actions

## Decision-Support Output

### Human-Readable Explanations
Examples:
- "High risk due to opposing crowd flows near exit gate"
- "Rapid density increase detected in last 60 seconds"
- "Motion instability detected across multiple regions"

### Recommended Actions
- Redirect crowd flow
- Open additional exits
- Deploy personnel
- Implement crowd control barriers
- Prepare emergency response team

## Installation

1. **Clone or download the project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Create necessary directories**:
The system will automatically create `data/`, `logs/`, and `videos/` directories on first run.

## Usage

### 1. Start the API Server

In one terminal:
```bash
python run_api.py
```

The API will be available at `http://localhost:8000`

### 2. Start the Video Processor

In another terminal:
```bash
python run_processor.py
```

This will:
- Create simulated video feeds for testing
- Process frames and send analysis to API
- Generate alerts when risks are detected

### 3. Launch the Dashboard

In a third terminal:
```bash
python run_dashboard.py
```

Or directly:
```bash
streamlit run dashboard/main.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Configuration

Edit `config.py` to customize:

- **Risk thresholds**: Safe, moderate, critical levels
- **Analysis parameters**: Frame skip rate, grid size, thresholds
- **Camera configuration**: Add/modify camera locations
- **Dashboard settings**: Update intervals, history points
- **API settings**: Host, port configuration

## Project Structure

```
crowd_management/
├── analytics/
│   ├── __init__.py
│   ├── crowd_analyzer.py      # Core analysis engine
│   └── risk_predictor.py      # ML-based trend prediction
├── backend/
│   ├── __init__.py
│   └── api.py                 # FastAPI backend
├── services/
│   ├── __init__.py
│   ├── video_processor.py     # Multi-camera processor
│   └── video_simulator.py     # Synthetic feed generator
├── dashboard/
│   └── main.py                # Streamlit dashboard
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── run_api.py                 # API server launcher
├── run_processor.py           # Processor launcher
├── run_dashboard.py           # Dashboard launcher
└── README.md                  # This file
```

## Sample Alert Messages

### Critical Alert Example
```
🚨 CRITICAL ALERT
Camera: cam_001 | Location: East Exit Gate
Risk Index: 0.87
Cause: Density Surge + Opposing Crowd Flows
Time: 2024-01-15 14:32:15

Recommended Actions:
• Redirect crowd flow to reduce opposing movements
• Open additional exits to reduce congestion
• Deploy personnel to guide traffic direction
```

### Warning Alert Example
```
⚠️ WARNING
Camera: cam_002 | Location: West Concourse
Risk Index: 0.52
Cause: Motion Instability
```

## Sample Analysis Report

```json
{
  "camera_id": "cam_001",
  "risk_index": 0.75,
  "alert_level": "moderate",
  "risk_factors": {
    "density_surge": 0.68,
    "motion_instability": 0.42,
    "directional_conflict": 0.15,
    "average_density": 0.45,
    "peak_motion": 0.58
  },
  "trend": "increasing",
  "rate_of_change": 0.05,
  "timestamp": "2024-01-15T14:32:15"
}
```

## Design Principles

- **Large fonts**: Easy to read from distance
- **High contrast colors**: Clear visual distinction
- **Minimal clutter**: Focus on critical information
- **Real-time updates**: WebSocket-based live data
- **Stress-tested design**: Optimized for high-pressure decision making

## Future Enhancements

- Mobile dashboard for field officers
- Historical incident analysis
- Integration with actual CCTV systems
- Machine learning model training on real data
- Automated alert escalation
- Integration with emergency response systems

## License

This project is provided as-is for demonstration and educational purposes.

## Support

For issues or questions, please refer to the code documentation or create an issue in the project repository.
