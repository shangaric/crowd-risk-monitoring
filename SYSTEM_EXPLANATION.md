# Crowd Risk Monitoring Platform - System Explanation

## 1. System-Level Overview

The **Live Crowd Risk Monitoring Platform** is a comprehensive real-time surveillance and analysis system designed to detect and alert on emergent crowd hazards. The system aggregates multiple CCTV camera feeds, continuously analyzes crowd behavior patterns, and provides actionable intelligence to authorities.

### Core Capabilities

- **Multi-Feed Aggregation**: Simultaneously processes multiple camera streams
- **Real-Time Analysis**: Frame-by-frame crowd behavior analysis with minimal latency
- **Hazard Detection**: Identifies three critical risk indicators:
  - **Stampede Risk**: Detected through directional conflict analysis
  - **Congestion**: Identified via density surge detection
  - **Panic Movement**: Recognized through motion instability patterns
- **Visual Risk Mapping**: Color-coded heatmaps overlay on camera feeds
- **Automated Alerting**: Generates alerts with severity levels and explanations
- **Decision Support**: Provides human-readable analysis and recommended actions

## 2. Technology Stack & Justification

### Python
**Purpose**: Core analytics and system logic
**Justification**: 
- Extensive ecosystem for computer vision (OpenCV, NumPy)
- Excellent for rapid prototyping and deployment
- Strong support for async operations (asyncio)
- Easy integration with web frameworks

### OpenCV
**Purpose**: Video ingestion, frame processing, optical flow calculation
**Justification**:
- Industry-standard computer vision library
- Efficient video capture and processing
- Built-in optical flow algorithms (Farneback method)
- Background subtraction capabilities (MOG2)
- Cross-platform support

### NumPy
**Purpose**: Density, motion, and risk computations
**Justification**:
- High-performance array operations
- Essential for image processing (frames as arrays)
- Efficient mathematical operations on large datasets
- Foundation for all numerical computations

### Scikit-learn
**Purpose**: Smoothing and short-term risk trend prediction
**Justification**:
- Lightweight ML models (Linear Regression)
- Minimal computational overhead
- Good for time-series trend prediction
- Explainable predictions

### FastAPI
**Purpose**: Backend services and alert APIs
**Justification**:
- High-performance async framework
- Automatic API documentation
- Built-in WebSocket support
- Type safety with Pydantic
- Easy to deploy and scale

### Streamlit
**Purpose**: Real-time control-room dashboard
**Justification**:
- Rapid dashboard development
- Built-in real-time update capabilities
- Easy integration with Plotly for visualizations
- Minimal code for professional UI
- Perfect for operational dashboards

### WebSockets
**Purpose**: Live data updates
**Justification**:
- Low-latency bidirectional communication
- Real-time push notifications
- Efficient for continuous data streams
- Better than polling for live updates

### Local Storage / Logs
**Purpose**: Incident history and reporting
**Justification**:
- JSON-based storage for flexibility
- Easy to query and analyze
- Can be extended to databases later
- Logs for debugging and audit trails

## 3. ML & Analytics Process

### Input Stage
- **Source**: Multiple live or recorded CCTV video feeds
- **Format**: Standard video formats (MP4, AVI) or RTSP streams
- **Processing Rate**: Configurable frame skipping (default: every 5th frame)

### Feature Extraction Pipeline

#### For Each Camera Frame:

**1. Crowd Density per Region**
- **Method**: Background subtraction using MOG2 algorithm
- **Process**:
  - Apply background subtractor to isolate moving objects
  - Perform morphological operations (close/open) to clean noise
  - Calculate foreground pixel ratio per grid region
  - Normalize to 0-1 scale
- **Output**: Density value (0.0 = empty, 1.0 = maximum density)

**2. Motion Intensity**
- **Method**: Optical flow using Farneback dense optical flow
- **Process**:
  - Convert frame to grayscale
  - Calculate flow vectors between consecutive frames
  - Compute magnitude of flow vectors: `√(dx² + dy²)`
  - Average magnitude per region
  - Normalize to 0-1 scale
- **Output**: Motion intensity (0.0 = static, 1.0 = high motion)

**3. Directional Conflict**
- **Method**: Vector angle analysis
- **Process**:
  - Extract flow vectors from optical flow
  - Calculate angles: `atan2(dy, dx)`
  - Compare angles between vector pairs
  - Detect opposing flows (angles differ by ~180°)
  - Count conflicting pairs
  - Normalize to 0-1 scale
- **Output**: Conflict score (0.0 = uniform flow, 1.0 = high conflict)

### Risk Computation

#### Local Risk Score (Per Region)
```
risk_score = 0.4 × density_risk^1.5 + 
             0.3 × motion_risk^1.2 + 
             0.3 × conflict_risk^1.8
```

**Weighting Rationale**:
- Density (40%): Base indicator of crowd presence
- Motion (30%): Indicates activity level
- Conflict (30%): Most dangerous - indicates stampede risk
- **Non-linear scaling**: Exponential risk for high values (conflict^1.8 is most severe)

#### Crowd Risk Index (Overall)
```
base_risk = mean(all_region_risks)

if max_conflict > threshold:
    base_risk *= 1.3  # Boost for conflict

if density_surge > 0.6:
    base_risk *= 1.2  # Boost for density

risk_index = min(base_risk, 1.0)
```

### Explainable Risk Factors

The system provides five explainable components:

1. **Density Surge**: Peak density above threshold (0.4)
2. **Motion Instability**: Standard deviation of motion across regions
3. **Directional Conflict**: Maximum conflict score across all regions
4. **Average Density**: Mean density across all regions
5. **Peak Motion**: Maximum motion intensity detected

### Alert Levels

- **Safe**: Risk index < 0.3 (Green)
- **Moderate**: Risk index 0.3 - 0.8 (Yellow/Orange)
- **Critical**: Risk index ≥ 0.8 (Red)

## 4. Dashboard Outputs

### A. Multi-Camera View Panel
- **Layout**: Grid display (2 columns)
- **Per Camera Display**:
  - Camera ID (e.g., "cam_001")
  - Location (e.g., "East Exit Gate")
  - Current timestamp
  - Risk index (0-1 scale)
  - Alert level badge (color-coded)
- **Update Frequency**: Every 1 second

### B. Risk Heatmap Overlay
- **Visualization**: 4×4 grid heatmap
- **Color Coding**:
  - **Green**: Risk < 0.3 (Safe)
  - **Yellow**: Risk 0.3 - 0.8 (Moderate)
  - **Red**: Risk ≥ 0.8 (Critical)
- **Overlay Method**: Semi-transparent color overlay on video frame
- **Grid Display**: Separate heatmap visualization below video feed

### C. Crowd Risk Index Graph
- **Type**: Time-series line chart (Plotly)
- **Features**:
  - Multiple camera feeds on same graph
  - Color-coded by camera
  - Threshold lines (moderate and critical)
  - Interactive hover details
  - 100-point history window
- **Updates**: Real-time as new data arrives

### D. Alerts Panel
- **Layout**: Vertical list, sorted by severity
- **Per Alert Display**:
  - Severity badge (Warning/Critical)
  - Camera ID
  - Location
  - Risk score
  - Status indicator (Active/Resolved)
  - Timestamp
  - Detected cause
- **Maximum Display**: Top 10 most recent alerts
- **Color Coding**: 
  - Critical: Red background, white text
  - Warning: Orange background, white text

### E. Critical Alert Details Section
- **Trigger**: When critical alerts are active
- **Display Format**: Expandable sections
- **Information Shown**:
  - Camera ID and Location
  - Risk Index value (large, prominent)
  - Severity level
  - Detected cause (e.g., "Density Surge + Opposing Crowd Flows")
  - Timestamp
  - Risk factor breakdown (table)
  - Recommended actions (bullet list)

## 5. Decision-Support Output

### Human-Readable Explanations

**Examples**:
- "High risk due to opposing crowd flows near exit gate"
- "Rapid density increase detected in last 60 seconds"
- "Motion instability detected across multiple regions"
- "Density surge + directional conflict detected"

### Recommended Actions

**Based on Risk Factors**:

**If Directional Conflict > 0.3**:
- Redirect crowd flow to reduce opposing movements
- Deploy personnel to guide traffic direction

**If Density Surge > 0.5**:
- Open additional exits to reduce congestion
- Implement crowd control barriers

**If Motion Instability > 0.4**:
- Monitor for panic indicators
- Prepare emergency response team

**Default**:
- Continue monitoring
- Maintain current crowd control measures

## 6. Mobile / Field View (Future Enhancement)

**Planned Features**:
- Simplified mobile dashboard
- Heatmap snapshot
- Current risk level
- Alert messages
- Push notifications
- GPS location integration

## 7. Design & Usability Rules

### Visual Design Principles

1. **Large Fonts**: 
   - Headers: 24px minimum
   - Critical alerts: 20px
   - Body text: 16px minimum

2. **High Contrast Colors**:
   - Safe: Green (#00FF00)
   - Moderate: Orange/Yellow (#FFAA00)
   - Critical: Red (#FF0000)
   - Background: Light gray (#f0f0f0)
   - Text: Black on light, white on dark

3. **Minimal Clutter**:
   - Clear section separation
   - Focused information display
   - No unnecessary decorations
   - Important information prominently displayed

4. **Stress-Tested Design**:
   - Critical information always visible
   - No hidden menus for alerts
   - One-click access to details
   - Clear visual hierarchy

## 8. Sample Outputs

### Sample Alert Message

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

### Sample Analysis Report

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
  "regions": [
    {
      "id": 0,
      "risk_score": 0.65,
      "density": 0.52,
      "motion_intensity": 0.48,
      "directional_conflict": 0.12
    },
    ...
  ],
  "trend": "increasing",
  "rate_of_change": 0.05,
  "prediction": 0.78,
  "timestamp": "2024-01-15T14:32:15"
}
```

## System Architecture

```
┌─────────────────┐
│  CCTV Cameras   │
│  (Multiple)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Video Processor │
│  (OpenCV)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Crowd Analyzer  │
│  (ML Pipeline)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend│
│  (REST + WS)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Dashboard│ │  Alerts │
│(Streamlit)│ │  System │
└────────┘ └──────────┘
```

## Real-World Usability

This system is designed for:
- **Control room operators**: Real-time monitoring
- **Security personnel**: Quick risk assessment
- **Emergency responders**: Rapid decision making
- **Event managers**: Proactive crowd control

The system prioritizes:
- **Clarity**: Easy to understand at a glance
- **Speed**: Minimal latency in detection
- **Accuracy**: Explainable, transparent analysis
- **Actionability**: Clear recommendations
