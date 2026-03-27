import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
from faker import Faker

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="Bangalore Metro OT Security Dashboard (Live Demo)",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Bangalore Metro Data
# ---------------------------
# Real station names and lines
purple_line_stations = [
    "Baiyappanahalli", "Indiranagar", "Swami Vivekananda Road", "Trinity",
    "Mahatma Gandhi Road", "Cubbon Park", "Vidhana Soudha", "Sir M. Visvesvaraya",
    "National College", "Lalbagh", "South End Circle", "Jayanagar",
    "Rashtreeya Vidyalaya Road", "Banashankari", "Jaya Prakash Nagar", "Yelachenahalli"
]

green_line_stations = [
    "Nagasandra", "Dasarahalli", "Jalahalli", "Peenya Industry", "Peenya",
    "Goraguntepalya", "Yeshwanthpur", "Sandal Soap Factory", "Mahalakshmi",
    "Rajajinagar", "Kuvempu Road", "Srirampura", "Sampige Road",
    "National College", "Chickpet", "Krishna Rajendra Market", "Banashankari"
]

# Combine with depots and control centers
assets = {
    "Stations": purple_line_stations + green_line_stations,
    "Depots": ["Peenya Depot", "Baiyappanahalli Depot", "Kengeri Depot"],
    "Control Centers": ["Central Control Room - Byappanahalli", "Backup Control Center - Peenya"]
}

# Coordinates for approximate locations (realistic for map)
station_coords = {
    "Baiyappanahalli": (12.9726, 77.6644),
    "Indiranagar": (12.9784, 77.6408),
    "Swami Vivekananda Road": (12.9825, 77.6224),
    "Trinity": (12.9821, 77.6158),
    "Mahatma Gandhi Road": (12.9762, 77.6078),
    "Cubbon Park": (12.9753, 77.5950),
    "Vidhana Soudha": (12.9799, 77.5908),
    "Sir M. Visvesvaraya": (12.9769, 77.5869),
    "National College": (12.9533, 77.5727),
    "Lalbagh": (12.9496, 77.5849),
    "South End Circle": (12.9386, 77.5853),
    "Jayanagar": (12.9289, 77.5879),
    "Rashtreeya Vidyalaya Road": (12.9197, 77.5928),
    "Banashankari": (12.9255, 77.5584),
    "Jaya Prakash Nagar": (12.9178, 77.5660),
    "Yelachenahalli": (12.9050, 77.5633),
    "Nagasandra": (13.0353, 77.5320),
    "Dasarahalli": (13.0252, 77.5333),
    "Jalahalli": (13.0178, 77.5359),
    "Peenya Industry": (13.0109, 77.5259),
    "Peenya": (13.0109, 77.5259),
    "Goraguntepalya": (13.0002, 77.5318),
    "Yeshwanthpur": (12.9957, 77.5495),
    "Sandal Soap Factory": (12.9901, 77.5531),
    "Mahalakshmi": (12.9874, 77.5545),
    "Rajajinagar": (12.9862, 77.5557),
    "Kuvempu Road": (12.9843, 77.5568),
    "Srirampura": (12.9826, 77.5622),
    "Sampige Road": (12.9830, 77.5653),
    "Chickpet": (12.9745, 77.5740),
    "Krishna Rajendra Market": (12.9695, 77.5738),
}
# Add depots and control centers
station_coords.update({
    "Peenya Depot": (13.0100, 77.5230),
    "Baiyappanahalli Depot": (12.9730, 77.6700),
    "Kengeri Depot": (12.9100, 77.4830),
    "Central Control Room - Byappanahalli": (12.9730, 77.6700),
    "Backup Control Center - Peenya": (13.0100, 77.5230)
})

# ---------------------------
# Helper functions for dynamic simulation
# ---------------------------
fake = Faker()

def generate_initial_scada_data():
    """Generate initial batch of SCADA data for all assets."""
    data = []
    for asset, lat_lon in station_coords.items():
        asset_type = "Station"
        if "Depot" in asset:
            asset_type = "Depot"
        elif "Control" in asset:
            asset_type = "Control Center"

        data.append({
            "asset": asset,
            "type": asset_type,
            "latitude": lat_lon[0],
            "longitude": lat_lon[1],
            "timestamp": datetime.now(),
            "traction_power_kw": np.random.normal(800, 200) if asset_type == "Station" else np.random.normal(2000, 400),
            "signaling_health": np.random.uniform(85, 100),
            "comm_latency_ms": np.random.uniform(10, 150),
            "network_bandwidth_mbps": np.random.uniform(50, 500),
            "cyber_risk_score": np.random.randint(0, 100),
            "anomalies": np.random.choice([0, 1, 2], p=[0.85, 0.10, 0.05])
        })
    return pd.DataFrame(data)

def generate_new_scada_reading():
    """Simulate one new SCADA reading for a random asset."""
    asset = random.choice(list(station_coords.keys()))
    asset_type = "Station"
    if "Depot" in asset:
        asset_type = "Depot"
    elif "Control" in asset:
        asset_type = "Control Center"
    lat, lon = station_coords[asset]

    return {
        "asset": asset,
        "type": asset_type,
        "latitude": lat,
        "longitude": lon,
        "timestamp": datetime.now(),
        "traction_power_kw": np.random.normal(800, 200) if asset_type == "Station" else np.random.normal(2000, 400),
        "signaling_health": np.random.uniform(85, 100),
        "comm_latency_ms": np.random.uniform(10, 150),
        "network_bandwidth_mbps": np.random.uniform(50, 500),
        "cyber_risk_score": np.random.randint(0, 100),
        "anomalies": np.random.choice([0, 1, 2], p=[0.85, 0.10, 0.05])
    }

def generate_initial_traffic_data():
    """Initial batch of network traffic flows."""
    protocols = ['Modbus/TCP', 'DNP3', 'IEC 60870-5-104', 'OPC UA', 'Profinet', 'EtherNet/IP']
    sources = list(station_coords.keys())
    n = 200
    data = []
    for i in range(n):
        src = random.choice(sources)
        dst = random.choice(sources)
        protocol = random.choice(protocols)
        bytes_sent = random.randint(1024, 50*1024*1024)
        packets = random.randint(10, 5000)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))
        anomaly = random.choice([0, 1, 2])
        data.append({
            "timestamp": timestamp,
            "src": src,
            "dst": dst,
            "protocol": protocol,
            "bytes": bytes_sent,
            "packets": packets,
            "anomaly_score": anomaly
        })
    return pd.DataFrame(data)

def generate_new_traffic_flow():
    """Simulate one new network flow."""
    protocols = ['Modbus/TCP', 'DNP3', 'IEC 60870-5-104', 'OPC UA', 'Profinet', 'EtherNet/IP']
    sources = list(station_coords.keys())
    src = random.choice(sources)
    dst = random.choice(sources)
    protocol = random.choice(protocols)
    bytes_sent = random.randint(1024, 50*1024*1024)
    packets = random.randint(10, 5000)
    anomaly = random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
    return {
        "timestamp": datetime.now(),
        "src": src,
        "dst": dst,
        "protocol": protocol,
        "bytes": bytes_sent,
        "packets": packets,
        "anomaly_score": anomaly
    }

def generate_initial_security_events(num_events=100):
    """Initial batch of SIEM events."""
    severities = ['Informational', 'Low', 'Medium', 'High', 'Critical']
    event_types = [
        "Unauthorized Access to ATC System",
        "PLC Firmware Change (Unexpected)",
        "Modbus Command Injection Attempt",
        "Abnormal Signaling Traffic",
        "User Privilege Escalation on SCADA",
        "Failed Login from Unknown IP",
        "Port Scan on Control Network",
        "Malware Detected on HMI",
        "Ransomware Activity in Depot Network",
        "RTU Configuration Change",
        "Communication Link Degradation",
        "Backdoor Detected in Historian DB"
    ]
    mitre_techniques = {
        "Unauthorized Access to ATC System": "T0882 (Exploit Public-Facing Application)",
        "PLC Firmware Change (Unexpected)": "T0800 (Firmware Manipulation)",
        "Modbus Command Injection Attempt": "T0830 (Man-in-the-Middle)",
        "Abnormal Signaling Traffic": "T0860 (Network Denial of Service)",
        "User Privilege Escalation on SCADA": "T0819 (Exploitation for Privilege Escalation)",
        "Failed Login from Unknown IP": "T0843 (Brute Force)",
        "Port Scan on Control Network": "T0855 (Network Service Scanning)",
        "Malware Detected on HMI": "T0862 (Malware)",
        "Ransomware Activity in Depot Network": "T0862 (Malware)",
        "RTU Configuration Change": "T0800 (Firmware Manipulation)",
        "Communication Link Degradation": "T0806 (Data Destruction)",
        "Backdoor Detected in Historian DB": "T0881 (Backdoor)"
    }
    assets = list(station_coords.keys())

    events = []
    for i in range(num_events):
        severity = np.random.choice(severities, p=[0.2, 0.3, 0.25, 0.15, 0.1])
        event_type = random.choice(event_types)
        asset = random.choice(assets)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))
        events.append({
            "event_id": f"SEC-{i+1000}",
            "timestamp": timestamp,
            "severity": severity,
            "event_type": event_type,
            "asset": asset,
            "mitre_technique": mitre_techniques.get(event_type, "Unknown"),
            "description": fake.sentence(nb_words=10),
            "status": random.choice(["Open", "Investigating", "Closed"])
        })
    return pd.DataFrame(events)

def generate_new_security_event():
    """Simulate one new security event."""
    severities = ['Informational', 'Low', 'Medium', 'High', 'Critical']
    event_types = [
        "Unauthorized Access to ATC System",
        "PLC Firmware Change (Unexpected)",
        "Modbus Command Injection Attempt",
        "Abnormal Signaling Traffic",
        "User Privilege Escalation on SCADA",
        "Failed Login from Unknown IP",
        "Port Scan on Control Network",
        "Malware Detected on HMI",
        "Ransomware Activity in Depot Network",
        "RTU Configuration Change",
        "Communication Link Degradation",
        "Backdoor Detected in Historian DB"
    ]
    mitre_techniques = {
        "Unauthorized Access to ATC System": "T0882 (Exploit Public-Facing Application)",
        "PLC Firmware Change (Unexpected)": "T0800 (Firmware Manipulation)",
        "Modbus Command Injection Attempt": "T0830 (Man-in-the-Middle)",
        "Abnormal Signaling Traffic": "T0860 (Network Denial of Service)",
        "User Privilege Escalation on SCADA": "T0819 (Exploitation for Privilege Escalation)",
        "Failed Login from Unknown IP": "T0843 (Brute Force)",
        "Port Scan on Control Network": "T0855 (Network Service Scanning)",
        "Malware Detected on HMI": "T0862 (Malware)",
        "Ransomware Activity in Depot Network": "T0862 (Malware)",
        "RTU Configuration Change": "T0800 (Firmware Manipulation)",
        "Communication Link Degradation": "T0806 (Data Destruction)",
        "Backdoor Detected in Historian DB": "T0881 (Backdoor)"
    }
    assets = list(station_coords.keys())

    severity = np.random.choice(severities, p=[0.2, 0.3, 0.25, 0.15, 0.1])
    event_type = random.choice(event_types)
    asset = random.choice(assets)
    event_id = f"SEC-{random.randint(10000, 99999)}"
    return {
        "event_id": event_id,
        "timestamp": datetime.now(),
        "severity": severity,
        "event_type": event_type,
        "asset": asset,
        "mitre_technique": mitre_techniques.get(event_type, "Unknown"),
        "description": fake.sentence(nb_words=10),
        "status": random.choice(["Open", "Investigating"])
    }

# ---------------------------
# Initialize session state with data
# ---------------------------
if "scada_data" not in st.session_state:
    st.session_state.scada_data = generate_initial_scada_data()
if "traffic_data" not in st.session_state:
    st.session_state.traffic_data = generate_initial_traffic_data()
if "events_data" not in st.session_state:
    st.session_state.events_data = generate_initial_security_events()

# Keep last N records to prevent memory bloat
MAX_SCADA_RECORDS = 2000
MAX_TRAFFIC_RECORDS = 5000
MAX_EVENTS = 2000

# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.header("Live Simulation")
auto_refresh = st.sidebar.checkbox("Enable auto-refresh (live mode)", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", min_value=2, max_value=15, value=5)

# Filter by asset type
asset_type_filter = st.sidebar.multiselect(
    "Asset Type",
    options=["Station", "Depot", "Control Center"],
    default=["Station", "Depot", "Control Center"]
)

severity_filter = st.sidebar.multiselect(
    "Event Severity",
    options=["Informational", "Low", "Medium", "High", "Critical"],
    default=["High", "Critical"]
)

# ---------------------------
# Dynamic update function
# ---------------------------
def update_data():
    """Append new simulated data points to session state."""
    # Update SCADA
    new_scada = generate_new_scada_reading()
    st.session_state.scada_data = pd.concat(
        [st.session_state.scada_data, pd.DataFrame([new_scada])], ignore_index=True
    )
    # Trim
    if len(st.session_state.scada_data) > MAX_SCADA_RECORDS:
        st.session_state.scada_data = st.session_state.scada_data.tail(MAX_SCADA_RECORDS)

    # Update traffic
    new_traffic = generate_new_traffic_flow()
    st.session_state.traffic_data = pd.concat(
        [st.session_state.traffic_data, pd.DataFrame([new_traffic])], ignore_index=True
    )
    if len(st.session_state.traffic_data) > MAX_TRAFFIC_RECORDS:
        st.session_state.traffic_data = st.session_state.traffic_data.tail(MAX_TRAFFIC_RECORDS)

    # Update events (occasionally, e.g., 20% chance per update)
    if random.random() < 0.3:  # 30% chance to add a new event
        new_event = generate_new_security_event()
        st.session_state.events_data = pd.concat(
            [st.session_state.events_data, pd.DataFrame([new_event])], ignore_index=True
        )
        if len(st.session_state.events_data) > MAX_EVENTS:
            st.session_state.events_data = st.session_state.events_data.tail(MAX_EVENTS)

# ---------------------------
# Main dashboard UI
# ---------------------------
st.title("🚇 Bangalore Metro OT Security & Network Monitoring Dashboard (Live Demo)")
st.markdown("Unified view of SCADA health, network traffic, and security events across the Namma Metro network. **Data updates dynamically.**")

# If auto-refresh is on, update data after a delay and rerun
if auto_refresh:
    update_data()
    # Use a placeholder to force rerun after interval
    placeholder = st.empty()
    time.sleep(refresh_interval)
    st.rerun()

# Apply filters
scada_filtered = st.session_state.scada_data[st.session_state.scada_data["type"].isin(asset_type_filter)]
events_filtered = st.session_state.events_data[st.session_state.events_data["severity"].isin(severity_filter)]

# ---------------------------
# KPIs
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Assets", len(scada_filtered))
with col2:
    # Latest anomalies (last 5 minutes)
    recent = scada_filtered[scada_filtered["timestamp"] > datetime.now() - timedelta(minutes=5)]
    total_anomalies = recent[recent["anomalies"] > 0].shape[0]
    st.metric("Assets with Anomalies (last 5 min)", total_anomalies)
with col3:
    avg_risk = scada_filtered["cyber_risk_score"].mean()
    st.metric("Average Cyber Risk Score", f"{avg_risk:.1f}/100")
with col4:
    critical_events = events_filtered[events_filtered["severity"] == "Critical"].shape[0]
    st.metric("Critical Security Events (last 24h)", critical_events, delta="Alert" if critical_events > 10 else "Normal")

# ---------------------------
# Map View of Asset Health (latest reading per asset)
# ---------------------------
st.subheader("📍 Asset Health Map (Latest Cyber Risk)")
latest_scada = scada_filtered.sort_values("timestamp").groupby("asset").last().reset_index()
fig_map = px.scatter_mapbox(
    latest_scada,
    lat="latitude",
    lon="longitude",
    color="cyber_risk_score",
    size="signaling_health",
    hover_name="asset",
    hover_data={
        "traction_power_kw": True,
        "comm_latency_ms": True,
        "network_bandwidth_mbps": True,
        "anomalies": True
    },
    color_continuous_scale="RdYlGn_r",
    size_max=15,
    zoom=11,
    height=500,
    title="Cyber Risk Score by Asset (Green=Low Risk, Red=High Risk)"
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

# ---------------------------
# SCADA Metrics Overview (last 24h trends)
# ---------------------------
st.subheader("📊 SCADA Metrics Overview (Last 24h)")
col1, col2 = st.columns(2)

# Prepare time-series data (last 24h)
scada_last24 = scada_filtered[scada_filtered["timestamp"] > datetime.now() - timedelta(hours=24)]

with col1:
    # Traction power over time for a few assets (sample)
    sample_assets = scada_last24["asset"].unique()[:5]  # first 5 assets
    power_ts = scada_last24[scada_last24["asset"].isin(sample_assets)]
    fig_power_ts = px.line(power_ts, x="timestamp", y="traction_power_kw", color="asset",
                           title="Traction Power Consumption (kW) - Selected Assets")
    st.plotly_chart(fig_power_ts, use_container_width=True)
with col2:
    # Signaling health distribution
    fig_signal = px.histogram(scada_last24, x="signaling_health", nbins=20,
                              title="Signaling System Health Distribution")
    st.plotly_chart(fig_signal, use_container_width=True)

# ---------------------------
# Network Traffic Analysis
# ---------------------------
st.subheader("🌐 OT Network Traffic (Last 24h)")
traffic_last24 = st.session_state.traffic_data[
    st.session_state.traffic_data["timestamp"] > datetime.now() - timedelta(hours=24)
]

col1, col2 = st.columns(2)
with col1:
    # Traffic by protocol
    protocol_counts = traffic_last24["protocol"].value_counts().reset_index()
    protocol_counts.columns = ["Protocol", "Count"]
    fig_proto = px.pie(protocol_counts, values="Count", names="Protocol",
                       title="Protocol Distribution")
    st.plotly_chart(fig_proto, use_container_width=True)
with col2:
    # Anomaly score distribution in traffic
    anomaly_dist = traffic_last24["anomaly_score"].value_counts().sort_index()
    fig_anom = px.bar(x=anomaly_dist.index, y=anomaly_dist.values,
                      labels={"x": "Anomaly Score", "y": "Flows"},
                      title="Traffic Anomaly Score Distribution")
    st.plotly_chart(fig_anom, use_container_width=True)

# Bandwidth usage over time
traffic_last24["hour"] = traffic_last24["timestamp"].dt.floor("H")
hourly_bandwidth = traffic_last24.groupby("hour")["bytes"].sum() / (1024*1024)  # MB
fig_bw = px.line(x=hourly_bandwidth.index, y=hourly_bandwidth.values,
                 labels={"x": "Time", "y": "Total Bandwidth (MB)"},
                 title="Network Bandwidth Usage (Last 24h)")
st.plotly_chart(fig_bw, use_container_width=True)

# ---------------------------
# SIEM Events Table & Timeline
# ---------------------------
st.subheader("🚨 OT Security Events (SIEM)")
events_last24 = events_filtered[
    events_filtered["timestamp"] > datetime.now() - timedelta(hours=24)
]

# Event timeline
events_last24["date"] = events_last24["timestamp"].dt.date
daily_events = events_last24.groupby(["date", "severity"]).size().reset_index(name="count")
fig_timeline = px.bar(daily_events, x="date", y="count", color="severity",
                      title="Security Events by Severity (Last 24h)")
st.plotly_chart(fig_timeline, use_container_width=True)

# Display events table with expandable details
st.dataframe(
    events_last24[["timestamp", "severity", "event_type", "asset", "mitre_technique", "status"]].sort_values("timestamp", ascending=False),
    use_container_width=True,
    height=400
)

# ---------------------------
# Executive Summary & Recommendations
# ---------------------------
st.subheader("📈 Executive Summary")
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔍 Key Observations")
    critical_assets = scada_last24[scada_last24["anomalies"] == 2]
    if not critical_assets.empty:
        st.warning(f"**{len(critical_assets)} assets** have critical anomalies in the last 24h.")
    top_risk = latest_scada.nlargest(5, "cyber_risk_score")[["asset", "cyber_risk_score"]]
    st.write("**Top 5 High-Risk Assets (Current):**")
    st.dataframe(top_risk, use_container_width=True)
with col2:
    st.markdown("### 📌 Recommended Actions")
    st.write("""
    - Investigate assets with critical anomalies and high cyber risk scores.
    - Focus on protocols with high anomaly rates (check Modbus/TCP for injection attempts).
    - Review SIEM events with MITRE techniques for potential attacker behavior.
    - Enhance monitoring on high-risk stations (Banashankari, Peenya, etc.).
    - Schedule firmware integrity checks for PLCs and RTUs.
    """)

# Footer
st.markdown("---")
st.caption("Data refreshes dynamically every few seconds. This is a simulation for demonstration. Actual deployment would ingest from SCADA servers and SIEM.")