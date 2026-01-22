"""
FastAPI backend for crowd risk monitoring
Provides REST API and WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List
import json
import asyncio
from datetime import datetime
import config
from analytics.crowd_analyzer import FrameAnalysis

app = FastAPI(title="Crowd Risk Monitoring API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Store current analysis results
current_analyses: Dict[str, dict] = {}

# Store alerts
alerts: List[dict] = []


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Crowd Risk Monitoring API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/api/cameras")
async def get_cameras():
    """Get list of configured cameras"""
    return {"cameras": list(config.CAMERAS.values())}


@app.get("/api/analysis/{camera_id}")
async def get_analysis(camera_id: str):
    """Get latest analysis for a camera"""
    if camera_id in current_analyses:
        return current_analyses[camera_id]
    return JSONResponse(
        status_code=404,
        content={"error": f"Camera {camera_id} not found"}
    )


@app.get("/api/analysis")
async def get_all_analyses():
    """Get latest analysis for all cameras"""
    return {"analyses": current_analyses}


@app.get("/api/alerts")
async def get_alerts():
    """Get current alerts"""
    return {"alerts": alerts[-config.DASHBOARD_CONFIG["max_alerts"]:]}


@app.post("/api/analysis/{camera_id}")
async def update_analysis(camera_id: str, analysis: dict):
    """Update analysis results for a camera"""
    analysis["timestamp"] = datetime.now().isoformat()
    current_analyses[camera_id] = analysis
    
    # Check for alerts
    if analysis.get("alert_level") in ["moderate", "critical"]:
        _create_alert(camera_id, analysis)
    
    # Broadcast to WebSocket clients
    await broadcast_update(camera_id, analysis)
    
    return {"status": "updated"}


def _create_alert(camera_id: str, analysis: dict):
    """Create alert from analysis"""
    camera_info = config.CAMERAS.get(camera_id, {})
    
    alert = {
        "id": f"{camera_id}_{datetime.now().timestamp()}",
        "camera_id": camera_id,
        "location": camera_info.get("location", "Unknown"),
        "severity": analysis.get("alert_level", "moderate").upper(),
        "risk_index": analysis.get("risk_index", 0.0),
        "timestamp": datetime.now().isoformat(),
        "status": "active",
        "risk_factors": analysis.get("risk_factors", {}),
        "cause": _generate_alert_cause(analysis)
    }
    
    # Add to alerts (remove old alerts for same camera if cooldown active)
    alerts.append(alert)
    
    # Keep only recent alerts
    if len(alerts) > config.DASHBOARD_CONFIG["max_alerts"]:
        alerts.pop(0)


def _generate_alert_cause(analysis: dict) -> str:
    """Generate human-readable cause description"""
    risk_factors = analysis.get("risk_factors", {})
    causes = []
    
    if risk_factors.get("density_surge", 0) > 0.5:
        causes.append("Density Surge")
    
    if risk_factors.get("directional_conflict", 0) > 0.3:
        causes.append("Opposing Crowd Flows")
    
    if risk_factors.get("motion_instability", 0) > 0.4:
        causes.append("Motion Instability")
    
    if not causes:
        return "Elevated Risk Detected"
    
    return " + ".join(causes)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "initial_state",
            "analyses": current_analyses,
            "alerts": alerts[-10:]
        })
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
            # Connection will be closed by client or on error
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcast_update(camera_id: str, analysis: dict):
    """Broadcast update to all WebSocket clients"""
    message = {
        "type": "analysis_update",
        "camera_id": camera_id,
        "analysis": analysis
    }
    
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_cameras": len(current_analyses),
        "active_alerts": len([a for a in alerts if a["status"] == "active"]),
        "websocket_connections": len(active_connections)
    }
