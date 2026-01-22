"""
Video processing service that handles multiple camera feeds
"""
import cv2
import numpy as np
from typing import Dict, Optional, Callable
from datetime import datetime
import asyncio
import config
from analytics.crowd_analyzer import CrowdAnalyzer, FrameAnalysis
from analytics.risk_predictor import RiskPredictor


class VideoProcessor:
    """
    Processes video feeds from multiple cameras
    Can work with live feeds or recorded videos
    """
    
    def __init__(self):
        self.analyzers: Dict[str, CrowdAnalyzer] = {}
        self.predictors: Dict[str, RiskPredictor] = {}
        self.captures: Dict[str, cv2.VideoCapture] = {}
        self.is_running = False
        self.frame_callbacks: Dict[str, Callable] = {}
    
    def add_camera(self, camera_id: str, source: str):
        """
        Add a camera feed
        source: video file path, camera index, or RTSP URL
        """
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video source: {source}")
        
        self.captures[camera_id] = cap
        self.analyzers[camera_id] = CrowdAnalyzer(
            grid_size=config.ANALYSIS_CONFIG["region_grid_size"]
        )
        self.predictors[camera_id] = RiskPredictor(
            history_window=config.ANALYSIS_CONFIG["history_window"]
        )
    
    def set_frame_callback(self, camera_id: str, callback: Callable):
        """Set callback function for processed frames"""
        self.frame_callbacks[camera_id] = callback
    
    async def process_camera(self, camera_id: str):
        """Process frames from a single camera"""
        if camera_id not in self.captures:
            return
        
        cap = self.captures[camera_id]
        analyzer = self.analyzers[camera_id]
        predictor = self.predictors[camera_id]
        
        frame_count = 0
        frame_skip = config.ANALYSIS_CONFIG["frame_skip"]
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                # End of video or connection lost
                await asyncio.sleep(1)
                continue
            
            # Skip frames for performance
            if frame_count % (frame_skip + 1) != 0:
                frame_count += 1
                continue
            
            # Analyze frame
            analysis = analyzer.analyze_frame(frame, camera_id)
            
            # Update predictor
            predictor.update(analysis.overall_risk_index, analysis.timestamp)
            
            # Get prediction
            prediction = predictor.predict_next(lookahead_seconds=10)
            trend = predictor.get_trend()
            rate_of_change = predictor.get_rate_of_change()
            
            # Prepare result
            result = {
                "camera_id": camera_id,
                "risk_index": analysis.overall_risk_index,
                "alert_level": analysis.alert_level,
                "risk_factors": analysis.risk_factors,
                "regions": [
                    {
                        "id": r.region_id,
                        "risk_score": r.risk_score,
                        "density": r.density,
                        "motion_intensity": r.motion_intensity,
                        "directional_conflict": r.directional_conflict
                    }
                    for r in analysis.regions
                ],
                "prediction": prediction,
                "trend": trend,
                "rate_of_change": rate_of_change,
                "timestamp": analysis.timestamp.isoformat()
            }
            
            # Call callback if set
            if camera_id in self.frame_callbacks:
                await self.frame_callbacks[camera_id](result, frame)
            
            frame_count += 1
            await asyncio.sleep(0.1)  # Small delay to prevent overwhelming
    
    async def start_processing(self):
        """Start processing all cameras"""
        self.is_running = True
        
        # Create tasks for each camera
        tasks = [
            self.process_camera(camera_id)
            for camera_id in self.captures.keys()
        ]
        
        await asyncio.gather(*tasks)
    
    def stop_processing(self):
        """Stop processing all cameras"""
        self.is_running = False
        
        # Release all captures
        for cap in self.captures.values():
            cap.release()
        
        self.captures.clear()
        self.analyzers.clear()
        self.predictors.clear()
    
    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Get current frame from a camera (for display)"""
        if camera_id not in self.captures:
            return None
        
        cap = self.captures[camera_id]
        ret, frame = cap.read()
        if ret:
            return frame
        return None
