"""Quick status check script"""
import requests
import json

try:
    # Check API health
    r = requests.get('http://localhost:8000/api/health', timeout=2)
    health = r.json()
    print("=" * 50)
    print("SYSTEM STATUS")
    print("=" * 50)
    print(f"API Status: {health['status']}")
    print(f"Active Cameras: {health['active_cameras']}")
    print(f"Active Alerts: {health['active_alerts']}")
    print(f"WebSocket Connections: {health['websocket_connections']}")
    print()
    
    # Check camera analyses
    r = requests.get('http://localhost:8000/api/analysis', timeout=2)
    analyses = r.json().get('analyses', {})
    print(f"Cameras with Data: {len(analyses)}")
    if analyses:
        print("\nCamera Details:")
        for cam_id, data in analyses.items():
            risk = data.get('risk_index', 0)
            level = data.get('alert_level', 'unknown')
            print(f"  {cam_id}: Risk={risk:.3f}, Level={level.upper()}")
    else:
        print("  (Video processor is still generating feeds...)")
    print()
    
    # Check alerts
    r = requests.get('http://localhost:8000/api/alerts', timeout=2)
    alerts = r.json().get('alerts', [])
    print(f"Total Alerts: {len(alerts)}")
    if alerts:
        active = [a for a in alerts if a.get('status') == 'active']
        print(f"Active Alerts: {len(active)}")
        for alert in active[:3]:
            print(f"  [{alert.get('severity')}] {alert.get('camera_id')}: {alert.get('cause')}")
    
    print("=" * 50)
    print("✅ API: http://localhost:8000")
    print("✅ Dashboard: http://localhost:8501")
    print("=" * 50)
    
except Exception as e:
    print(f"Error: {e}")
    print("API may still be starting up...")
