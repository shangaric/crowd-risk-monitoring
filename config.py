"""
Configuration settings for the Crowd Risk Monitoring Platform
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
VIDEOS_DIR = BASE_DIR / "videos"

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, VIDEOS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Risk thresholds
RISK_THRESHOLDS = {
    "safe": 0.3,
    "moderate": 0.6,
    "critical": 0.8
}

# Analysis parameters
ANALYSIS_CONFIG = {
    "frame_skip": 5,  # Process every 5th frame for performance
    "region_grid_size": (4, 4),  # Divide frame into 4x4 grid
    "density_threshold": 0.4,  # Crowd density threshold
    "motion_threshold": 0.3,  # Motion intensity threshold
    "conflict_threshold": 0.25,  # Directional conflict threshold
    "history_window": 60,  # Seconds of history to keep
    "alert_cooldown": 30,  # Seconds between same alerts
}

# Camera configuration
CAMERAS = {
    "cam_001": {
        "id": "cam_001",
        "location": "East Exit Gate",
        "description": "Main entrance monitoring"
    },
    "cam_002": {
        "id": "cam_002",
        "location": "West Concourse",
        "description": "Central area monitoring"
    },
    "cam_003": {
        "id": "cam_003",
        "location": "North Plaza",
        "description": "Outdoor plaza monitoring"
    },
    "cam_004": {
        "id": "cam_004",
        "location": "South Corridor",
        "description": "Indoor corridor monitoring"
    }
}

# Dashboard settings
DASHBOARD_CONFIG = {
    "update_interval": 1.0,  # Update every second
    "max_alerts": 20,
    "graph_history_points": 100,
}

# API settings
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "websocket_port": 8001,
}
