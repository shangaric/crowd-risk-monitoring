"""
Streamlit Dashboard for Crowd Risk Monitoring
Implements all required dashboard components
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import time
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

from PIL import Image
import io
import cv2


# Page configuration
st.set_page_config(
    page_title="Crowd Risk Monitoring",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visibility
st.markdown("""
<style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .critical-alert {
        background-color: #ff4444;
        color: white;
        padding: 15px;
        border-radius: 5px;
        font-size: 20px;
        font-weight: bold;
    }
    .moderate-alert {
        background-color: #ffaa00;
        color: white;
        padding: 15px;
        border-radius: 5px;
        font-size: 18px;
    }
    .safe-status {
        background-color: #44ff44;
        color: black;
        padding: 15px;
        border-radius: 5px;
        font-size: 18px;
    }
    .metric-card {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_BASE = "http://localhost:8000"


@st.cache_data(ttl=1)
def fetch_analyses():
    """Fetch current analyses from API"""
    try:
        response = requests.get(f"{API_BASE}/api/analysis", timeout=1)
        if response.status_code == 200:
            return response.json().get("analyses", {})
    except:
        pass
    return {}


@st.cache_data(ttl=1)
def fetch_alerts():
    """Fetch current alerts from API"""
    try:
        response = requests.get(f"{API_BASE}/api/alerts", timeout=1)
        if response.status_code == 200:
            return response.json().get("alerts", [])
    except:
        pass
    return []


def get_risk_color(risk_index: float) -> str:
    """Get color based on risk index"""
    if risk_index >= config.RISK_THRESHOLDS["critical"]:
        return "#FF0000"  # Red
    elif risk_index >= config.RISK_THRESHOLDS["moderate"]:
        return "#FFAA00"  # Orange/Yellow
    else:
        return "#00FF00"  # Green


def create_heatmap_overlay(frame, regions, grid_size=(4, 4)):
    """Create heatmap overlay on frame"""
    h, w = frame.shape[:2]
    rows, cols = grid_size
    region_h = h // rows
    region_w = w // cols
    
    overlay = frame.copy()
    
    for region in regions:
        region_id = region["id"]
        risk_score = region["risk_score"]
        
        i = region_id // cols
        j = region_id % cols
        
        y1, y2 = i * region_h, (i + 1) * region_h
        x1, x2 = j * region_w, (j + 1) * region_w
        
        # Get color
        color = get_risk_color(risk_score)
        color_bgr = tuple(int(color[i:i+2], 16) for i in (5, 3, 1))[::-1]
        
        # Create semi-transparent overlay
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color_bgr, -1)
    
    # Blend with original
    alpha = 0.4
    result = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)
    return result


def main():
    """Main dashboard function"""
    
    # Header
    st.title("🚨 Crowd Risk Monitoring Dashboard")
    st.markdown("---")
    
    # Sidebar controls
    with st.sidebar:
        st.header("System Controls")
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 1)
        
        if st.button("🔄 Manual Refresh"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.subheader("System Status")
        try:
            response = requests.get(f"{API_BASE}/api/health", timeout=1)
            if response.status_code == 200:
                health = response.json()
                st.success(f"✅ API: {health.get('status', 'unknown')}")
                st.info(f"📹 Active Cameras: {health.get('active_cameras', 0)}")
                st.warning(f"⚠️ Active Alerts: {health.get('active_alerts', 0)}")
        except:
            st.error("❌ API Connection Failed")
    
    # Fetch data
    analyses = fetch_analyses()
    alerts = fetch_alerts()
    
    # A. Multi-Camera View Panel
    st.header("📹 Multi-Camera View")
    
    if not analyses:
        st.warning("No camera feeds available. Please start the video processor.")
    else:
        # Display cameras in grid
        camera_ids = list(analyses.keys())
        num_cameras = len(camera_ids)
        
        if num_cameras > 0:
            cols = st.columns(min(2, num_cameras))
            
            for idx, camera_id in enumerate(camera_ids):
                col = cols[idx % 2]
                analysis = analyses[camera_id]
                
                with col:
                    camera_info = config.CAMERAS.get(camera_id, {})
                    location = camera_info.get("location", "Unknown")
                    
                    # Camera header
                    risk_index = analysis.get("risk_index", 0.0)
                    alert_level = analysis.get("alert_level", "safe")
                    color = get_risk_color(risk_index)
                    
                    st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <h3 style="color: {'white' if risk_index > 0.5 else 'black'}; margin: 0;">
                            📷 {camera_id} - {location}
                        </h3>
                        <p style="color: {'white' if risk_index > 0.5 else 'black'}; margin: 5px 0;">
                            Risk Index: {risk_index:.2f} | Status: {alert_level.upper()}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Placeholder for video frame (in real implementation, would show actual frame)
                    timestamp = analysis.get("timestamp", datetime.now().isoformat())
                    st.caption(f"Last Update: {timestamp}")
                    
                    # B. Risk Heatmap Overlay (simulated)
                    # In real implementation, this would show actual video frame with overlay
                    st.info("📺 Video Feed with Risk Heatmap Overlay")
                    st.caption("Green = Safe | Yellow = Moderate | Red = Critical")
                    
                    # Show region risk breakdown
                    regions = analysis.get("regions", [])
                    if regions:
                        region_risks = [r["risk_score"] for r in regions]
                        risk_matrix = np.array(region_risks).reshape(config.ANALYSIS_CONFIG["region_grid_size"])
                        
                        fig = px.imshow(
                            risk_matrix,
                            color_continuous_scale=["green", "yellow", "red"],
                            aspect="auto",
                            title="Risk Heatmap (4x4 Grid)"
                        )
                        fig.update_layout(height=200)
                        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # C. Crowd Risk Index Graph
    st.header("📊 Crowd Risk Index - Time Series")
    
    if analyses:
        # Create time series data
        risk_data = []
        for camera_id, analysis in analyses.items():
            camera_info = config.CAMERAS.get(camera_id, {})
            location = camera_info.get("location", camera_id)
            risk_data.append({
                "timestamp": analysis.get("timestamp", datetime.now().isoformat()),
                "camera": location,
                "risk_index": analysis.get("risk_index", 0.0),
                "alert_level": analysis.get("alert_level", "safe")
            })
        
        if risk_data:
            df = pd.DataFrame(risk_data)
            
            fig = go.Figure()
            
            for camera in df["camera"].unique():
                camera_df = df[df["camera"] == camera]
                fig.add_trace(go.Scatter(
                    x=camera_df["timestamp"],
                    y=camera_df["risk_index"],
                    mode='lines+markers',
                    name=camera,
                    line=dict(width=3)
                ))
            
            # Add threshold lines
            fig.add_hline(
                y=config.RISK_THRESHOLDS["critical"],
                line_dash="dash",
                line_color="red",
                annotation_text="Critical Threshold"
            )
            fig.add_hline(
                y=config.RISK_THRESHOLDS["moderate"],
                line_dash="dash",
                line_color="orange",
                annotation_text="Moderate Threshold"
            )
            
            fig.update_layout(
                title="Crowd Risk Index Evolution",
                xaxis_title="Time",
                yaxis_title="Risk Index (0-1)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for risk index graph")
    
    st.markdown("---")
    
    # D. Alerts Panel
    st.header("⚠️ Alerts Panel")
    
    if alerts:
        # Filter active alerts
        active_alerts = [a for a in alerts if a.get("status") == "active"]
        active_alerts = sorted(active_alerts, key=lambda x: x.get("risk_index", 0), reverse=True)
        
        if active_alerts:
            for alert in active_alerts[:10]:  # Show top 10
                severity = alert.get("severity", "WARNING")
                risk_index = alert.get("risk_index", 0.0)
                camera_id = alert.get("camera_id", "Unknown")
                location = alert.get("location", "Unknown")
                cause = alert.get("cause", "Unknown")
                timestamp = alert.get("timestamp", "")
                
                if severity == "CRITICAL":
                    st.markdown(f"""
                    <div class="critical-alert">
                        🚨 CRITICAL ALERT<br>
                        Camera: {camera_id} | Location: {location}<br>
                        Risk Index: {risk_index:.2f}<br>
                        Cause: {cause}<br>
                        Time: {timestamp}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="moderate-alert">
                        ⚠️ WARNING<br>
                        Camera: {camera_id} | Location: {location}<br>
                        Risk Index: {risk_index:.2f}<br>
                        Cause: {cause}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.success("✅ No active alerts")
    else:
        st.info("No alerts to display")
    
    st.markdown("---")
    
    # E. Critical Alert Details Section
    st.header("🔍 Critical Alert Details")
    
    critical_alerts = [a for a in alerts if a.get("severity") == "CRITICAL" and a.get("status") == "active"]
    
    if critical_alerts:
        for alert in critical_alerts:
            with st.expander(f"🚨 {alert.get('camera_id')} - {alert.get('location')}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Risk Index", f"{alert.get('risk_index', 0.0):.2f}")
                    st.metric("Severity", alert.get('severity', 'UNKNOWN'))
                    st.metric("Camera ID", alert.get('camera_id', 'Unknown'))
                
                with col2:
                    st.metric("Location", alert.get('location', 'Unknown'))
                    st.metric("Detected Cause", alert.get('cause', 'Unknown'))
                    st.metric("Timestamp", alert.get('timestamp', 'Unknown'))
                
                # Risk factors breakdown
                risk_factors = alert.get('risk_factors', {})
                if risk_factors:
                    st.subheader("Risk Factor Breakdown")
                    factor_df = pd.DataFrame([
                        {"Factor": k.replace("_", " ").title(), "Value": v}
                        for k, v in risk_factors.items()
                    ])
                    st.dataframe(factor_df, use_container_width=True)
                
                # Recommended actions
                st.subheader("Recommended Actions")
                recommendations = generate_recommendations(alert)
                for rec in recommendations:
                    st.markdown(f"• {rec}")
    else:
        st.success("✅ No critical alerts at this time")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


def generate_recommendations(alert: dict) -> list:
    """Generate human-readable recommendations based on alert"""
    recommendations = []
    risk_factors = alert.get('risk_factors', {})
    
    if risk_factors.get('directional_conflict', 0) > 0.3:
        recommendations.append("Redirect crowd flow to reduce opposing movements")
        recommendations.append("Deploy personnel to guide traffic direction")
    
    if risk_factors.get('density_surge', 0) > 0.5:
        recommendations.append("Open additional exits to reduce congestion")
        recommendations.append("Implement crowd control barriers")
    
    if risk_factors.get('motion_instability', 0) > 0.4:
        recommendations.append("Monitor for panic indicators")
        recommendations.append("Prepare emergency response team")
    
    if not recommendations:
        recommendations.append("Continue monitoring")
        recommendations.append("Maintain current crowd control measures")
    
    return recommendations


if __name__ == "__main__":
    main()
