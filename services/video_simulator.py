"""
Video feed simulator for testing and demonstration
Generates synthetic crowd scenes with varying risk levels
"""
import cv2
import numpy as np
from typing import Tuple
import random
import config


class VideoSimulator:
    """
    Simulates video feeds with synthetic crowd scenes
    Useful for testing and demonstration without real cameras
    """
    
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.frame_count = 0
        
        # Simulation parameters
        self.crowd_density = 0.3
        self.motion_intensity = 0.2
        self.conflict_level = 0.1
        
        # Background
        self.background = self._create_background()
    
    def _create_background(self) -> np.ndarray:
        """Create a static background"""
        bg = np.ones((self.height, self.width, 3), dtype=np.uint8) * 200
        # Add some structure (like a floor pattern)
        for i in range(0, self.height, 20):
            cv2.line(bg, (0, i), (self.width, i), (180, 180, 180), 1)
        return bg
    
    def generate_frame(self, risk_level: str = "safe") -> np.ndarray:
        """
        Generate a synthetic frame with crowd
        risk_level: "safe", "moderate", "critical"
        """
        frame = self.background.copy()
        
        # Adjust parameters based on risk level
        if risk_level == "critical":
            self.crowd_density = min(self.crowd_density + 0.05, 0.9)
            self.motion_intensity = min(self.motion_intensity + 0.1, 1.0)
            self.conflict_level = min(self.conflict_level + 0.1, 0.8)
        elif risk_level == "moderate":
            self.crowd_density = min(self.crowd_density + 0.02, 0.6)
            self.motion_intensity = min(self.motion_intensity + 0.05, 0.7)
            self.conflict_level = min(self.conflict_level + 0.05, 0.5)
        else:
            # Gradual decay towards safe levels
            self.crowd_density = max(self.crowd_density - 0.01, 0.2)
            self.motion_intensity = max(self.motion_intensity - 0.02, 0.1)
            self.conflict_level = max(self.conflict_level - 0.02, 0.0)
        
        # Add some randomness
        self.crowd_density += random.uniform(-0.05, 0.05)
        self.crowd_density = max(0.1, min(1.0, self.crowd_density))
        
        # Draw crowd as moving blobs
        num_people = int(self.crowd_density * 100)
        
        for _ in range(num_people):
            # Random position
            x = random.randint(20, self.width - 20)
            y = random.randint(20, self.height - 20)
            
            # Movement based on conflict level
            if self.conflict_level > 0.3:
                # Opposing flows - some move left, some right
                direction = 1 if random.random() > 0.5 else -1
                x += int(direction * self.motion_intensity * 10 * np.sin(self.frame_count * 0.1))
            else:
                # Uniform flow
                x += int(self.motion_intensity * 5 * np.cos(self.frame_count * 0.1))
                y += int(self.motion_intensity * 5 * np.sin(self.frame_count * 0.1))
            
            x = max(10, min(self.width - 10, x))
            y = max(10, min(self.height - 10, y))
            
            # Draw person as ellipse
            color = self._get_color_for_risk(risk_level)
            cv2.ellipse(frame, (x, y), (8, 12), 0, 0, 360, color, -1)
            cv2.ellipse(frame, (x, y), (8, 12), 0, 0, 360, (0, 0, 0), 1)
        
        self.frame_count += 1
        return frame
    
    def _get_color_for_risk(self, risk_level: str) -> Tuple[int, int, int]:
        """Get color based on risk level"""
        if risk_level == "critical":
            return (0, 0, 255)  # Red
        elif risk_level == "moderate":
            return (0, 165, 255)  # Orange
        else:
            return (0, 255, 0)  # Green
    
    def create_video_file(self, output_path: str, duration_seconds: int = 60, 
                         fps: int = 30):
        """Create a video file with varying risk levels"""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (self.width, self.height))
        
        risk_sequence = []
        # Create a sequence that varies risk
        for i in range(duration_seconds * fps):
            if i < duration_seconds * fps * 0.3:
                risk_sequence.append("safe")
            elif i < duration_seconds * fps * 0.6:
                risk_sequence.append("moderate")
            else:
                risk_sequence.append("critical")
        
        random.shuffle(risk_sequence)
        
        for risk in risk_sequence:
            frame = self.generate_frame(risk)
            out.write(frame)
        
        out.release()
