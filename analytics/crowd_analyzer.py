"""
Core crowd analysis engine using OpenCV and NumPy
Implements density, motion, and directional conflict detection
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import config


@dataclass
class RegionAnalysis:
    """Analysis results for a single region"""
    region_id: int
    density: float  # 0-1 scale
    motion_intensity: float  # 0-1 scale
    directional_conflict: float  # 0-1 scale
    risk_score: float  # 0-1 scale
    flow_direction: Tuple[float, float]  # Average flow vector


@dataclass
class FrameAnalysis:
    """Complete analysis for a single frame"""
    timestamp: datetime
    camera_id: str
    overall_risk_index: float  # 0-1 scale
    regions: List[RegionAnalysis]
    risk_factors: Dict[str, float]  # Explainable risk components
    alert_level: str  # "safe", "moderate", "critical"


class CrowdAnalyzer:
    """
    Main crowd analysis engine
    Processes video frames to extract crowd behavior metrics
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (4, 4)):
        self.grid_size = grid_size
        self.prev_gray = None
        self.prev_flow = None
        
        # Background subtractor for density estimation
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=True
        )
        
        # Optical flow parameters
        self.flow_params = dict(
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
    
    def analyze_frame(self, frame: np.ndarray, camera_id: str) -> FrameAnalysis:
        """
        Analyze a single frame and return comprehensive metrics
        """
        timestamp = datetime.now()
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        flow = self._calculate_optical_flow(gray)
        
        # Analyze regions
        regions = self._analyze_regions(frame, gray, flow)
        
        # Compute overall risk index
        risk_index, risk_factors = self._compute_risk_index(regions)
        
        # Determine alert level
        alert_level = self._determine_alert_level(risk_index)
        
        return FrameAnalysis(
            timestamp=timestamp,
            camera_id=camera_id,
            overall_risk_index=risk_index,
            regions=regions,
            risk_factors=risk_factors,
            alert_level=alert_level
        )
    
    def _calculate_optical_flow(self, gray: np.ndarray) -> Optional[np.ndarray]:
        """Calculate optical flow using Farneback method"""
        if self.prev_gray is None:
            self.prev_gray = gray
            return None
        
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray, None, **self.flow_params
        )
        
        self.prev_gray = gray
        return flow
    
    def _analyze_regions(self, frame: np.ndarray, gray: np.ndarray, 
                        flow: Optional[np.ndarray]) -> List[RegionAnalysis]:
        """Analyze each region in the grid"""
        h, w = gray.shape
        rows, cols = self.grid_size
        
        regions = []
        region_h = h // rows
        region_w = w // cols
        
        for i in range(rows):
            for j in range(cols):
                region_id = i * cols + j
                
                # Define region boundaries
                y1, y2 = i * region_h, (i + 1) * region_h
                x1, x2 = j * region_w, (j + 1) * region_w
                
                # Extract region
                region_gray = gray[y1:y2, x1:x2]
                region_frame = frame[y1:y2, x1:x2]
                
                # Calculate density
                density = self._calculate_density(region_frame)
                
                # Calculate motion metrics
                if flow is not None:
                    region_flow = flow[y1:y2, x1:x2]
                    motion_intensity, flow_direction = self._calculate_motion(region_flow)
                    directional_conflict = self._calculate_directional_conflict(region_flow)
                else:
                    motion_intensity = 0.0
                    flow_direction = (0.0, 0.0)
                    directional_conflict = 0.0
                
                # Compute region risk score
                risk_score = self._compute_region_risk(
                    density, motion_intensity, directional_conflict
                )
                
                regions.append(RegionAnalysis(
                    region_id=region_id,
                    density=density,
                    motion_intensity=motion_intensity,
                    directional_conflict=directional_conflict,
                    risk_score=risk_score,
                    flow_direction=flow_direction
                ))
        
        return regions
    
    def _calculate_density(self, region: np.ndarray) -> float:
        """
        Estimate crowd density using background subtraction
        Returns value between 0-1
        """
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(region)
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Calculate density as ratio of foreground pixels
        total_pixels = region.shape[0] * region.shape[1]
        foreground_pixels = np.sum(fg_mask > 0)
        density = min(foreground_pixels / (total_pixels * 0.5), 1.0)  # Cap at 1.0
        
        return float(density)
    
    def _calculate_motion(self, flow: np.ndarray) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate motion intensity and average flow direction
        Returns (intensity 0-1, (dx, dy))
        """
        # Calculate magnitude of flow vectors
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        
        # Normalize intensity (0-1 scale)
        max_magnitude = np.max(magnitude) if np.max(magnitude) > 0 else 1.0
        intensity = min(np.mean(magnitude) / (max_magnitude * 0.3), 1.0)
        
        # Calculate average flow direction
        mean_dx = np.mean(flow[..., 0])
        mean_dy = np.mean(flow[..., 1])
        
        # Normalize direction vector
        norm = np.sqrt(mean_dx**2 + mean_dy**2)
        if norm > 0:
            mean_dx /= norm
            mean_dy /= norm
        
        return float(intensity), (float(mean_dx), float(mean_dy))
    
    def _calculate_directional_conflict(self, flow: np.ndarray) -> float:
        """
        Detect opposing movement vectors (stampede risk indicator)
        Returns conflict score 0-1
        """
        if flow.size == 0:
            return 0.0
        
        # Get flow vectors
        dx = flow[..., 0].flatten()
        dy = flow[..., 1].flatten()
        
        # Calculate angles
        angles = np.arctan2(dy, dx)
        
        # Find opposing flows (angles differ by ~180 degrees)
        conflict_score = 0.0
        n_samples = min(len(angles), 100)  # Sample for performance
        
        for i in range(n_samples):
            for j in range(i + 1, n_samples):
                angle_diff = abs(angles[i] - angles[j])
                # Normalize to 0-π range
                if angle_diff > np.pi:
                    angle_diff = 2 * np.pi - angle_diff
                
                # High conflict if angles are nearly opposite (close to π)
                if angle_diff > np.pi * 0.7:  # > 126 degrees
                    conflict_score += 1.0
        
        # Normalize to 0-1 scale
        max_pairs = n_samples * (n_samples - 1) / 2
        conflict_score = min(conflict_score / max_pairs if max_pairs > 0 else 0, 1.0)
        
        return float(conflict_score)
    
    def _compute_region_risk(self, density: float, motion: float, 
                            conflict: float) -> float:
        """
        Compute risk score for a region using weighted combination
        """
        # Weighted risk components
        density_weight = 0.4
        motion_weight = 0.3
        conflict_weight = 0.3
        
        # Non-linear scaling for high values (exponential risk)
        density_risk = density ** 1.5
        motion_risk = motion ** 1.2
        conflict_risk = conflict ** 1.8  # Conflict is most dangerous
        
        risk = (
            density_weight * density_risk +
            motion_weight * motion_risk +
            conflict_weight * conflict_risk
        )
        
        return min(risk, 1.0)
    
    def _compute_risk_index(self, regions: List[RegionAnalysis]) -> Tuple[float, Dict[str, float]]:
        """
        Aggregate region risks into overall risk index
        Returns (risk_index, risk_factors)
        """
        if not regions:
            return 0.0, {}
        
        # Extract metrics
        densities = [r.density for r in regions]
        motions = [r.motion_intensity for r in regions]
        conflicts = [r.directional_conflict for r in regions]
        risks = [r.risk_score for r in regions]
        
        # Calculate risk factors
        max_density = max(densities)
        avg_density = np.mean(densities)
        max_motion = max(motions)
        max_conflict = max(conflicts)
        
        # Density surge detection
        density_surge = max_density if max_density > config.ANALYSIS_CONFIG["density_threshold"] else 0.0
        
        # Motion instability
        motion_std = np.std(motions)
        motion_instability = min(motion_std * 2, 1.0)
        
        # Overall risk index (weighted combination)
        base_risk = np.mean(risks)
        
        # Boost risk if critical factors present
        if max_conflict > config.ANALYSIS_CONFIG["conflict_threshold"]:
            base_risk *= 1.3
        
        if density_surge > 0.6:
            base_risk *= 1.2
        
        risk_index = min(base_risk, 1.0)
        
        risk_factors = {
            "density_surge": float(density_surge),
            "motion_instability": float(motion_instability),
            "directional_conflict": float(max_conflict),
            "average_density": float(avg_density),
            "peak_motion": float(max_motion)
        }
        
        return float(risk_index), risk_factors
    
    def _determine_alert_level(self, risk_index: float) -> str:
        """Determine alert level based on risk index"""
        if risk_index >= config.RISK_THRESHOLDS["critical"]:
            return "critical"
        elif risk_index >= config.RISK_THRESHOLDS["moderate"]:
            return "moderate"
        else:
            return "safe"
