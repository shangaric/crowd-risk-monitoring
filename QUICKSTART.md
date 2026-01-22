# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Running the System

The system consists of three components that need to run simultaneously:

### Terminal 1: API Server

```bash
python run_api.py
```

This starts the FastAPI backend on `http://localhost:8000`

### Terminal 2: Video Processor

```bash
python run_processor.py
```

This will:
- Generate simulated video feeds for testing
- Process frames and analyze crowd behavior
- Send results to the API

**Note**: The first run will take a minute to generate the video files.

### Terminal 3: Dashboard

```bash
python run_dashboard.py
```

Or directly:
```bash
streamlit run dashboard/main.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

## What to Expect

1. **Initial Setup**: The video processor creates simulated feeds (takes ~1 minute)

2. **Dashboard View**: You'll see:
   - Multi-camera view with risk indicators
   - Risk heatmaps for each camera
   - Time-series risk index graph
   - Alerts panel (will populate as risks are detected)
   - Critical alert details section

3. **Real-time Updates**: The dashboard refreshes every second showing:
   - Current risk levels
   - New alerts as they occur
   - Updated risk graphs

## Testing with Real Cameras

To use real camera feeds, modify `run_processor.py`:

```python
# Replace simulator with real camera
processor.add_camera("cam_001", 0)  # Use camera index 0
# Or RTSP URL:
processor.add_camera("cam_001", "rtsp://your-camera-url")
```

## Troubleshooting

**API Connection Failed**: 
- Ensure `run_api.py` is running
- Check that port 8000 is not in use

**No Video Feeds**:
- Wait for video generation to complete
- Check `data/` directory for generated videos

**Dashboard Not Updating**:
- Check that both API and processor are running
- Verify auto-refresh is enabled in sidebar

## Stopping the System

Press `Ctrl+C` in each terminal to stop the components gracefully.
