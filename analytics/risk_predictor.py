"""
Short-term risk trend prediction using lightweight ML
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import List, Optional
from datetime import datetime, timedelta
from collections import deque
import config


class RiskPredictor:
    """
    Predicts short-term risk trends using recent history
    Uses simple linear regression for trend prediction
    """
    
    def __init__(self, history_window: int = 60):
        self.history_window = history_window
        self.risk_history = deque(maxlen=history_window)
        self.timestamps = deque(maxlen=history_window)
        self.scaler = StandardScaler()
        self.model = LinearRegression()
    
    def update(self, risk_index: float, timestamp: datetime):
        """Add new risk measurement to history"""
        self.risk_history.append(risk_index)
        self.timestamps.append(timestamp)
    
    def predict_next(self, lookahead_seconds: int = 10) -> Optional[float]:
        """
        Predict risk index for next N seconds
        Returns None if insufficient history
        """
        if len(self.risk_history) < 10:
            return None
        
        # Prepare features (time series of risk values)
        X = np.array(list(self.risk_history)).reshape(-1, 1)
        y = np.array(list(self.risk_history))
        
        # Create time-based features
        if len(self.timestamps) > 1:
            time_diffs = []
            for i in range(1, len(self.timestamps)):
                diff = (self.timestamps[i] - self.timestamps[i-1]).total_seconds()
                time_diffs.append(diff)
            
            # Use recent trend
            recent_window = min(20, len(X))
            X_recent = X[-recent_window:]
            y_recent = y[-recent_window:]
            
            # Fit simple trend model
            try:
                X_time = np.arange(len(X_recent)).reshape(-1, 1)
                self.model.fit(X_time, y_recent)
                
                # Predict next value
                next_time = len(X_recent) + (lookahead_seconds / 1.0)  # Assuming 1 sec intervals
                prediction = self.model.predict([[next_time]])[0]
                
                # Clamp to valid range
                prediction = max(0.0, min(1.0, prediction))
                
                return float(prediction)
            except:
                return None
        
        return None
    
    def get_trend(self) -> str:
        """
        Get current trend direction
        Returns: "increasing", "decreasing", "stable"
        """
        if len(self.risk_history) < 5:
            return "stable"
        
        recent = list(self.risk_history)[-5:]
        if recent[-1] > recent[0] + 0.1:
            return "increasing"
        elif recent[-1] < recent[0] - 0.1:
            return "decreasing"
        else:
            return "stable"
    
    def get_rate_of_change(self) -> float:
        """
        Calculate rate of change in risk (per second)
        """
        if len(self.risk_history) < 2:
            return 0.0
        
        recent = list(self.risk_history)[-10:]
        if len(self.timestamps) >= 2:
            time_span = (self.timestamps[-1] - self.timestamps[-10]).total_seconds()
            if time_span > 0:
                risk_change = recent[-1] - recent[0]
                return risk_change / time_span
        
        return 0.0
