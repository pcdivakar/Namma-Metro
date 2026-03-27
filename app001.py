import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# Page configuration
st.set_page_config(
    page_title="Namma Metro OT Security SOC Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-critical {
        color: #DC2626;
        font-weight: bold;
    }
    .alert-high {
        color: #F97316;
        font-weight: bold;
    }
    .alert-medium {
        color: #F59E0B;
    }
    .alert-low {
        color: #10B981;
    }
    .zone-card {
        border-left: 4px solid #3B82F6;
        padding-left: 10px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Simulated Data Functions
# ---------------------------
def generate_ot_assets():
    """Generate a list of OT assets with status and zone."""
    assets = []
    zones = [
        {"name": "Level 0 - Field", "devices": ["PLC", "RTU", "IED", "Sensor", "Actuator"], "count_range": (30, 50)},
        {"name": "Level 1 - Control", "devices": ["PLC", "RTU", "IED", "Controller"], "count_range": (15, 25)},
        {"name": "Level 2 - Supervisory", "devices": ["HMI", "Engineering WS", "SCADA Server"], "count_range": (10, 15)},
        {"name": "Level 3 - Operations", "devices": ["Historian", "Application Server", "Terminal Server"], "count_range": (5, 10)},
        {"name": "Level 4 - Enterprise", "devices": ["Corporate Network", "DMZ"], "count_range": (3, 6)},
    ]
    for zone in zones:
        count = random.randint(*zone["count_range"])
        for i in range(count):
            device_type = random.choice(zone["devices"])
            status = random.choices(["Normal", "Warning", "Critical"], weights=[0.85, 0.10, 0.05])[0]
            assets.append({
                "Device ID": f"{device_type[:2].upper()}{i+1:03d}",
                "Type": device_type,
                "Zone": zone["name"],
                "Status": status,
                "Last Seen": datetime.now() - timedelta(seconds=random.randint(0, 300)),
                "Firmware Version": f"{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}"
            })
    return pd.DataFrame(assets)

def generate_protocol_stats():
    """Generate real-time protocol traffic statistics."""
    protocols = ["Modbus/TCP", "DNP3", "OPC DA", "IEC 61850", "Profinet", "Ethernet/IP"]
    stats = []
    for proto in protocols:
        packets = random.randint(100, 5000)
        anomalies = random.randint(0, int(packets * 0.02))  # up to 2% anomalies
        stats.append({
            "Protocol": proto,
            "Packets/sec": packets,
            "Anomalies/min": anomalies,
            "Threat Level": random.choices(["Low", "Medium", "High"], weights=[0.7, 0.2, 0.1])[0]
        })
    return pd.DataFrame(stats)

def generate_alerts():
    """Generate active security alerts for OT environment."""
    alert_types = [
        {"description": "Unauthorized Modbus write to PLC", "severity": "Critical", "mitre": "Tactic: Impact"},
        {"description": "Firmware change detected on RTU", "severity": "High", "mitre": "Tactic: Persistence"},
        {"description": "DNP3 unsolicited response from unknown IP", "severity": "High", "mitre": "Tactic: Discovery"},
        {"description": "HMI login failure (brute force)", "severity": "Medium", "mitre": "Tactic: Credential Access"},
        {"description": "Engineering workstation non‑standard software", "severity": "Medium", "mitre": "Tactic: Execution"},
        {"description": "PLC CPU overload (potential DoS)", "severity": "Critical", "mitre": "Tactic: Impact"},
        {"description": "Unencrypted OPC traffic in control zone", "severity": "Low", "mitre": "Tactic: Collection"},
    ]
    alerts = []
    for i in range(random.randint(5, 12)):
        alert = random.choice(alert_types)
        alerts.append({
            "Timestamp": datetime.now() - timedelta(minutes=random.randint(0, 120)),
            "Alert": alert["description"],
            "Severity": alert["severity"],
            "MITRE ATT&CK for ICS": alert["mitre"],
            "Status": random.choices(["Active", "Acknowledged", "Resolved"], weights=[0.7, 0.2, 0.1])[0]
        })
    alerts = sorted(alerts, key=lambda x: x["Timestamp"], reverse=True)
    return pd.DataFrame(alerts)

def generate_incident_trend(days=30):
    """Generate historical incident counts for trend analysis."""
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    data = []
    for dt in dates:
        critical = random.randint(0, 3)
        high = random.randint(0, 5)
        medium = random.randint(1, 8)
        low = random.randint(2, 12)
        data.append({"Date": dt, "Critical": critical, "High": high, "Medium": medium, "Low": low})
    return pd.DataFrame(data)

def generate_compliance_status():
    """Generate compliance metrics against IEC 62443."""
    categories = ["Patch Management", "Network Segmentation", "Access Control", "Logging & Monitoring", "Incident Response"]
    compliance = []
    for cat in categories:
        score = random.uniform(60, 100)
        status = "Pass" if score >= 80 else "Warning" if score >= 60 else "Fail"
        compliance.append({"Category": cat, "Compliance Score (%)": round(score, 1), "Status": status})
    return pd.DataFrame(compliance)

# ---------------------------
# Streamlit Layout
# ---------------------------
st.markdown('<div class="main-header">⚙️ Namma Metro OT Security SOC Dashboard</div>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header("Dashboard Controls")
    refresh_mode = st.radio("Refresh Mode", ["Manual", "Auto (10 sec)"])
    if refresh_mode == "Auto (10 sec)":
        auto_refresh = st.empty()
        # We'll handle auto-refresh via a placeholder later
    if st.button("Refresh Now"):
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("**Purdue Model Reference**")
    st.markdown("""
    - **Level 0**: Field devices (PLCs, RTUs, sensors)
    - **Level 1**: Local control
    - **Level 2**: Supervisory control (HMI, SCADA)
    - **Level 3**: Operations management
    - **Level 4**: Enterprise network
    """)

# Generate fresh data on each run (or auto-refresh)
if refresh_mode == "Auto (10 sec)":
    time.sleep(10)  # Simulate auto-refresh delay

assets_df = generate_ot_assets()
protocol_df = generate_protocol_stats()
alerts_df = generate_alerts()
incident_trend_df = generate_incident_trend()
compliance_df = generate_compliance_status()

# ---------------------------
# Key Metrics Row
# ---------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_devices = len(assets_df)
    critical_devices = len(assets_df[assets_df["Status"] == "Critical"])
    st.metric("Total OT Assets", total_devices, delta=f"{critical_devices} critical")
with col2:
    active_alerts = len(alerts_df[alerts_df["Status"] == "Active"])
    st.metric("Active Alerts", active_alerts, delta=None)
with col3:
    total_protocol_anomalies = protocol_df["Anomalies/min"].sum()
    st.metric("Protocol Anomalies/min", total_protocol_anomalies, delta=None)
with col4:
    # Average compliance score
    avg_compliance = compliance_df["Compliance Score (%)"].mean()
    st.metric("Avg. Compliance Score", f"{avg_compliance:.1f}%", delta=None)

st.markdown("---")

# ---------------------------
# Two columns: Asset Inventory + Protocol Stats
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 OT Asset Inventory by Zone")
    # Zone breakdown
    zone_status = assets_df.groupby(["Zone", "Status"]).size().reset_index(name="Count")
    fig_zone = px.bar(zone_status, x="Zone", y="Count", color="Status", 
                      title="Device Status per Purdue Zone",
                      color_discrete_map={"Normal": "#10B981", "Warning": "#F59E0B", "Critical": "#DC2626"})
    st.plotly_chart(fig_zone, use_container_width=True)
    
    # Asset table (show top 10)
    st.markdown("**Asset Details (sample)**")
    st.dataframe(assets_df.head(10), use_container_width=True)

with col2:
    st.subheader("📡 Protocol Traffic & Anomalies")
    fig_proto = px.bar(protocol_df, x="Protocol", y="Packets/sec", color="Threat Level",
                       title="Protocol Traffic Volume",
                       color_discrete_map={"Low": "#10B981", "Medium": "#F59E0B", "High": "#DC2626"})
    st.plotly_chart(fig_proto, use_container_width=True)
    
    st.dataframe(protocol_df, use_container_width=True)

st.markdown("---")

# ---------------------------
# Active Alerts + Compliance
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚨 Active Security Alerts")
    # Color code severity
    def severity_color(sev):
        if sev == "Critical":
            return "alert-critical"
        elif sev == "High":
            return "alert-high"
        elif sev == "Medium":
            return "alert-medium"
        else:
            return "alert-low"
    for _, row in alerts_df.iterrows():
        color_class = severity_color(row["Severity"])
        st.markdown(f"""
        <div class="zone-card">
            <span class="{color_class}">{row["Severity"]}</span> – {row["Alert"]}<br>
            <small>{row["Timestamp"].strftime("%H:%M:%S")} | MITRE: {row["MITRE ATT&CK for ICS"]} | Status: {row["Status"]}</small>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("📊 Compliance Status (IEC 62443)")
    fig_comply = px.bar(compliance_df, x="Category", y="Compliance Score (%)", color="Status",
                        color_discrete_map={"Pass": "#10B981", "Warning": "#F59E0B", "Fail": "#DC2626"},
                        text_auto=True)
    st.plotly_chart(fig_comply, use_container_width=True)

st.markdown("---")

# ---------------------------
# Incident Trends and Network Topology
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Incident Trends (Last 30 Days)")
    fig_trend = px.line(incident_trend_df, x="Date", y=["Critical", "High", "Medium", "Low"],
                        title="Daily Incident Count by Severity",
                        color_discrete_map={"Critical": "#DC2626", "High": "#F97316", "Medium": "#F59E0B", "Low": "#10B981"})
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("🌐 Network Topology (Purdue Model)")
    # Simple diagram using plotly graph objects
    zones = ["Level 4 - Enterprise", "Level 3 - Operations", "Level 2 - Supervisory", "Level 1 - Control", "Level 0 - Field"]
    # Simulate connections: each level connects to adjacent levels
    edges = []
    for i in range(len(zones)-1):
        edges.append((zones[i], zones[i+1]))
    # Create a directed graph layout
    pos = {z: (0, -i) for i, z in enumerate(zones)}  # vertical stack
    edge_x = []
    edge_y = []
    for edge in edges:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    node_x = [pos[z][0] for z in zones]
    node_y = [pos[z][1] for z in zones]
    fig_top = go.Figure()
    fig_top.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(color='#888', width=2), hoverinfo='none'))
    fig_top.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text', text=zones, textposition="middle right",
                                 marker=dict(size=20, color='#1E3A8A'), hoverinfo='text'))
    fig_top.update_layout(showlegend=False, xaxis_visible=False, yaxis_visible=False, height=400)
    st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

# ---------------------------
# Footer with last update time
# ---------------------------
st.caption(f"Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")