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
    page_title="Namma Metro OT Security Dashboard | Deloitte",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Custom CSS for branding
# ---------------------------
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            color: white;
        }
        .deloitte-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #86EFAC;
        }
        .metro-logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #FCD34D;
        }
        .clock {
            font-family: monospace;
            font-size: 1.2rem;
            background-color: #1E293B;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            color: #FCD34D;
            display: inline-block;
        }
        .kpi-card {
            background-color: #1F2937;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            text-align: center;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: bold;
            color: #FCD34D;
        }
        .kpi-label {
            font-size: 0.9rem;
            color: #9CA3AF;
        }
        .risk-high {
            color: #EF4444;
        }
        .risk-medium {
            color: #F59E0B;
        }
        .risk-low {
            color: #10B981;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Namma Metro Data (real stations, lines, zones)
# ---------------------------
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

# Depots & Control Centers
depots = ["Peenya Depot", "Baiyappanahalli Depot", "Kengeri Depot"]
control_centers = ["Central Control Room - Byappanahalli", "Backup Control Center - Peenya"]

# All assets (each station/depot/control center is a separate OT asset)
all_assets = purple_line_stations + green_line_stations + depots + control_centers

# Assign lines and zones
def get_line(asset):
    if asset in purple_line_stations:
        return "Purple Line"
    elif asset in green_line_stations:
        return "Green Line"
    elif asset in depots:
        return "Depot"
    else:
        return "Control Center"

def get_zone(asset):
    # Simple zone mapping based on approximate location
    if "Baiyappanahalli" in asset or "Indiranagar" in asset or "Trinity" in asset:
        return "East"
    elif "Nagasandra" in asset or "Peenya" in asset or "Yeshwanthpur" in asset:
        return "North"
    elif "Jayanagar" in asset or "Banashankari" in asset or "Yelachenahalli" in asset:
        return "South"
    elif "Cubbon Park" in asset or "Vidhana Soudha" in asset or "National College" in asset:
        return "Central"
    elif "Kengeri" in asset:
        return "West"
    else:
        return "Other"

# Coordinates (approximate)
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
    "Peenya Depot": (13.0100, 77.5230),
    "Baiyappanahalli Depot": (12.9730, 77.6700),
    "Kengeri Depot": (12.9100, 77.4830),
    "Central Control Room - Byappanahalli": (12.9730, 77.6700),
    "Backup Control Center - Peenya": (13.0100, 77.5230)
}

# ---------------------------
# Helper: generate initial asset data
# ---------------------------
fake = Faker()

def generate_initial_assets():
    assets = []
    for asset in all_assets:
        lat, lon = station_coords.get(asset, (12.97, 77.59))
        line = get_line(asset)
        zone = get_zone(asset)
        asset_type = "Station"
        if asset in depots:
            asset_type = "Depot"
        elif asset in control_centers:
            asset_type = "Control Center"

        # Simulate health and risk metrics
        health_score = np.random.uniform(70, 100)
        cyber_risk_score = np.random.randint(20, 95)
        vuln_count = np.random.randint(0, 15)
        patch_compliance = np.random.uniform(60, 100)
        criticality = np.random.choice(["High", "Medium", "Low"], p=[0.3, 0.5, 0.2])

        # Additional OT asset details
        plc_count = np.random.randint(5, 30) if asset_type == "Station" else np.random.randint(10, 50)
        rtu_count = np.random.randint(3, 20) if asset_type == "Station" else np.random.randint(5, 30)
        hmi_count = np.random.randint(1, 5)

        assets.append({
            "asset_name": asset,
            "type": asset_type,
            "line": line,
            "zone": zone,
            "latitude": lat,
            "longitude": lon,
            "health_score": health_score,
            "cyber_risk_score": cyber_risk_score,
            "vulnerability_count": vuln_count,
            "patch_compliance": patch_compliance,
            "criticality": criticality,
            "plc_count": plc_count,
            "rtu_count": rtu_count,
            "hmi_count": hmi_count,
            "last_assessed": datetime.now()
        })
    return pd.DataFrame(assets)

# ---------------------------
# Generate vulnerabilities per asset
# ---------------------------
def generate_vulnerabilities(assets_df):
    vulns = []
    cve_templates = [
        "CVE-2023-{0:04d}", "CVE-2024-{0:04d}", "CVE-2025-{0:04d}"
    ]
    for _, asset in assets_df.iterrows():
        num_vulns = asset["vulnerability_count"]
        for i in range(num_vulns):
            severity = np.random.choice(["Critical", "High", "Medium", "Low"], p=[0.1, 0.3, 0.4, 0.2])
            vulns.append({
                "asset_name": asset["asset_name"],
                "cve_id": random.choice(cve_templates).format(random.randint(1000, 9999)),
                "severity": severity,
                "description": fake.sentence(nb_words=8),
                "published_date": datetime.now() - timedelta(days=random.randint(0, 365)),
                "patch_available": np.random.choice([True, False], p=[0.7, 0.3])
            })
    return pd.DataFrame(vulns)

# ---------------------------
# Generate SIEM events
# ---------------------------
def generate_initial_events(assets_df, num_events=150):
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
        "Unauthorized Access to ATC System": "T0882",
        "PLC Firmware Change (Unexpected)": "T0800",
        "Modbus Command Injection Attempt": "T0830",
        "Abnormal Signaling Traffic": "T0860",
        "User Privilege Escalation on SCADA": "T0819",
        "Failed Login from Unknown IP": "T0843",
        "Port Scan on Control Network": "T0855",
        "Malware Detected on HMI": "T0862",
        "Ransomware Activity in Depot Network": "T0862",
        "RTU Configuration Change": "T0800",
        "Communication Link Degradation": "T0806",
        "Backdoor Detected in Historian DB": "T0881"
    }

    events = []
    for i in range(num_events):
        severity = np.random.choice(severities, p=[0.2, 0.3, 0.25, 0.15, 0.1])
        event_type = random.choice(event_types)
        asset = random.choice(assets_df["asset_name"].tolist())
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

# ---------------------------
# Dynamic update functions
# ---------------------------
def update_asset_health(assets_df):
    """Simulate new readings for a random asset."""
    idx = random.randint(0, len(assets_df)-1)
    asset = assets_df.iloc[idx].copy()
    # Random walk for health and risk
    asset["health_score"] += np.random.normal(0, 2)
    asset["health_score"] = np.clip(asset["health_score"], 0, 100)
    asset["cyber_risk_score"] += np.random.normal(0, 3)
    asset["cyber_risk_score"] = np.clip(asset["cyber_risk_score"], 0, 100)
    asset["last_assessed"] = datetime.now()
    # Small chance of vulnerability change
    if random.random() < 0.1:
        asset["vulnerability_count"] = max(0, asset["vulnerability_count"] + np.random.randint(-2, 3))
    assets_df.iloc[idx] = asset
    return assets_df

def update_vulnerabilities(vulns_df, assets_df):
    """Add or remove vulnerabilities occasionally."""
    # Remove some old vulns (simulate patching)
    if len(vulns_df) > 0 and random.random() < 0.2:
        idx = random.randint(0, len(vulns_df)-1)
        vulns_df = vulns_df.drop(idx).reset_index(drop=True)
    # Add new vulnerability
    if random.random() < 0.15:
        asset = random.choice(assets_df["asset_name"].tolist())
        new_vuln = {
            "asset_name": asset,
            "cve_id": f"CVE-{random.randint(2023,2025)}-{random.randint(1000,9999)}",
            "severity": np.random.choice(["Critical", "High", "Medium", "Low"], p=[0.1,0.3,0.4,0.2]),
            "description": fake.sentence(nb_words=8),
            "published_date": datetime.now(),
            "patch_available": np.random.choice([True, False])
        }
        vulns_df = pd.concat([vulns_df, pd.DataFrame([new_vuln])], ignore_index=True)
    return vulns_df

def update_events(events_df, assets_df):
    """Add a new event occasionally."""
    if random.random() < 0.3:
        new_event = generate_initial_events(assets_df, num_events=1).iloc[0]
        events_df = pd.concat([events_df, pd.DataFrame([new_event])], ignore_index=True)
        # Keep only last 2000 events
        if len(events_df) > 2000:
            events_df = events_df.tail(2000)
    return events_df

# ---------------------------
# Initialize session state
# ---------------------------
if "assets_df" not in st.session_state:
    st.session_state.assets_df = generate_initial_assets()
if "vulns_df" not in st.session_state:
    st.session_state.vulns_df = generate_vulnerabilities(st.session_state.assets_df)
if "events_df" not in st.session_state:
    st.session_state.events_df = generate_initial_events(st.session_state.assets_df)

# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.header("Live Simulation")
auto_refresh = st.sidebar.checkbox("Enable auto-refresh (live mode)", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", min_value=2, max_value=15, value=5)

# Filters
asset_type_filter = st.sidebar.multiselect(
    "Asset Type",
    options=["Station", "Depot", "Control Center"],
    default=["Station", "Depot", "Control Center"]
)
line_filter = st.sidebar.multiselect(
    "Line",
    options=["Purple Line", "Green Line", "Depot", "Control Center"],
    default=["Purple Line", "Green Line", "Depot", "Control Center"]
)
zone_filter = st.sidebar.multiselect(
    "Zone",
    options=["East", "North", "South", "Central", "West", "Other"],
    default=["East", "North", "South", "Central", "West"]
)

# ---------------------------
# Header with logos and clock
# ---------------------------
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown('<div class="deloitte-logo">Deloitte.</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metro-logo">Namma Metro OT Security Center</div>', unsafe_allow_html=True)
with col3:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'<div class="clock">🕒 {current_time}</div>', unsafe_allow_html=True)

# Live indicator if auto-refresh is on
if auto_refresh:
    st.sidebar.success("🟢 Live mode active - data updating every {} seconds".format(refresh_interval))

# ---------------------------
# Apply filters to assets
# ---------------------------
filtered_assets = st.session_state.assets_df[
    (st.session_state.assets_df["type"].isin(asset_type_filter)) &
    (st.session_state.assets_df["line"].isin(line_filter)) &
    (st.session_state.assets_df["zone"].isin(zone_filter))
]

# ---------------------------
# Dynamic update if auto-refresh
# ---------------------------
if auto_refresh:
    # Update each data source
    st.session_state.assets_df = update_asset_health(st.session_state.assets_df)
    st.session_state.vulns_df = update_vulnerabilities(st.session_state.vulns_df, st.session_state.assets_df)
    st.session_state.events_df = update_events(st.session_state.events_df, st.session_state.assets_df)
    # Wait and rerun
    time.sleep(refresh_interval)
    st.rerun()

# ---------------------------
# Tabs for the dashboard
# ---------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive Dashboard",
    "🖥️ OT Asset Health",
    "⚠️ Cyber Risk & Vulnerabilities",
    "📍 Station/Zone/Line Analysis",
    "🚨 SIEM Events & Alerts",
    "📋 Compliance & Recommendations"
])

# ---------------------------
# Tab 1: Executive Dashboard
# ---------------------------
with tab1:
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kpi-card"><div class="kpi-value">{}</div><div class="kpi-label">Total Assets</div></div>'.format(len(filtered_assets)), unsafe_allow_html=True)
    with col2:
        avg_health = filtered_assets["health_score"].mean()
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_health:.1f}</div><div class="kpi-label">Avg Health Score</div></div>', unsafe_allow_html=True)
    with col3:
        avg_risk = filtered_assets["cyber_risk_score"].mean()
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_risk:.1f}</div><div class="kpi-label">Avg Cyber Risk</div></div>', unsafe_allow_html=True)
    with col4:
        critical_events = st.session_state.events_df[st.session_state.events_df["severity"] == "Critical"].shape[0]
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{critical_events}</div><div class="kpi-label">Critical Events (24h)</div></div>', unsafe_allow_html=True)

    # Map
    st.subheader("Asset Health & Risk Map")
    fig_map = px.scatter_mapbox(
        filtered_assets,
        lat="latitude",
        lon="longitude",
        color="cyber_risk_score",
        size="health_score",
        hover_name="asset_name",
        hover_data={
            "type": True,
            "line": True,
            "zone": True,
            "vulnerability_count": True,
            "criticality": True
        },
        color_continuous_scale="RdYlGn_r",
        size_max=15,
        zoom=11,
        height=500
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

    # Top 5 risky assets
    st.subheader("Top 5 Assets by Cyber Risk")
    top_risk = filtered_assets.nlargest(5, "cyber_risk_score")[["asset_name", "type", "line", "cyber_risk_score", "health_score", "vulnerability_count"]]
    st.dataframe(top_risk, use_container_width=True)

    # Risk distribution by line and zone
    col1, col2 = st.columns(2)
    with col1:
        fig_line = px.box(filtered_assets, x="line", y="cyber_risk_score", color="line", title="Cyber Risk by Line")
        st.plotly_chart(fig_line, use_container_width=True)
    with col2:
        fig_zone = px.box(filtered_assets, x="zone", y="cyber_risk_score", color="zone", title="Cyber Risk by Zone")
        st.plotly_chart(fig_zone, use_container_width=True)

# ---------------------------
# Tab 2: OT Asset Health
# ---------------------------
with tab2:
    st.subheader("OT Asset Health Dashboard")
    # Display asset table with health metrics
    asset_display = filtered_assets[[
        "asset_name", "type", "line", "zone", "health_score", "cyber_risk_score",
        "vulnerability_count", "patch_compliance", "criticality",
        "plc_count", "rtu_count", "hmi_count", "last_assessed"
    ]].sort_values("cyber_risk_score", ascending=False)
    st.dataframe(asset_display, use_container_width=True)

    # Health trends (simulate by generating recent history)
    # For demonstration, we'll generate a fake time series for a selected asset
    asset_choice = st.selectbox("Select asset for health trend", filtered_assets["asset_name"].tolist())
    if asset_choice:
        # Simulate last 24 hours of health and risk for this asset
        history = []
        now = datetime.now()
        for i in range(24):
            ts = now - timedelta(hours=24-i)
            health = filtered_assets[filtered_assets["asset_name"] == asset_choice]["health_score"].values[0]
            risk = filtered_assets[filtered_assets["asset_name"] == asset_choice]["cyber_risk_score"].values[0]
            # Add some noise
            health += np.random.normal(0, 2)
            risk += np.random.normal(0, 3)
            health = np.clip(health, 0, 100)
            risk = np.clip(risk, 0, 100)
            history.append({"timestamp": ts, "health_score": health, "cyber_risk_score": risk})
        hist_df = pd.DataFrame(history)
        fig_trend = px.line(hist_df, x="timestamp", y=["health_score", "cyber_risk_score"],
                            title=f"Health and Risk Trend - {asset_choice}")
        st.plotly_chart(fig_trend, use_container_width=True)

    # Count of assets by type
    asset_counts = filtered_assets["type"].value_counts().reset_index()
    asset_counts.columns = ["Type", "Count"]
    fig_type = px.pie(asset_counts, values="Count", names="Type", title="Asset Distribution by Type")
    st.plotly_chart(fig_type, use_container_width=True)

# ---------------------------
# Tab 3: Cyber Risk & Vulnerabilities
# ---------------------------
with tab3:
    st.subheader("Cybersecurity Risk & Vulnerabilities")

    # Overall risk summary
    col1, col2 = st.columns(2)
    with col1:
        risk_cat = pd.cut(filtered_assets["cyber_risk_score"], bins=[0, 30, 70, 100], labels=["Low", "Medium", "High"]).value_counts()
        fig_risk_cat = px.bar(x=risk_cat.index, y=risk_cat.values, title="Risk Level Distribution", color=risk_cat.index)
        st.plotly_chart(fig_risk_cat, use_container_width=True)
    with col2:
        patch_summary = filtered_assets["patch_compliance"].describe()
        st.metric("Average Patch Compliance", f"{patch_summary['mean']:.1f}%")
        st.metric("Min Patch Compliance", f"{patch_summary['min']:.1f}%")
        st.metric("Max Patch Compliance", f"{patch_summary['max']:.1f}%")

    # Vulnerabilities table
    st.subheader("Vulnerabilities per Asset")
    # Merge vulnerabilities with assets to show asset details
    vuln_assets = st.session_state.vulns_df.merge(filtered_assets[["asset_name", "type", "line", "zone"]], on="asset_name", how="inner")
    st.dataframe(vuln_assets[["asset_name", "cve_id", "severity", "description", "published_date", "patch_available"]], use_container_width=True)

    # Top vulnerable assets
    top_vuln = vuln_assets["asset_name"].value_counts().reset_index()
    top_vuln.columns = ["Asset", "Vulnerability Count"]
    st.subheader("Top Assets by Vulnerability Count")
    st.dataframe(top_vuln.head(10), use_container_width=True)

# ---------------------------
# Tab 4: Station/Zone/Line Analysis
# ---------------------------
with tab4:
    st.subheader("Granular Analysis by Station, Zone, and Line")

    # Line-wise aggregations
    line_stats = filtered_assets.groupby("line").agg({
        "health_score": "mean",
        "cyber_risk_score": "mean",
        "vulnerability_count": "sum",
        "asset_name": "count"
    }).rename(columns={"asset_name": "asset_count"}).reset_index()
    st.subheader("Line-wise Summary")
    st.dataframe(line_stats, use_container_width=True)

    # Zone-wise aggregations
    zone_stats = filtered_assets.groupby("zone").agg({
        "health_score": "mean",
        "cyber_risk_score": "mean",
        "vulnerability_count": "sum",
        "asset_name": "count"
    }).rename(columns={"asset_name": "asset_count"}).reset_index()
    st.subheader("Zone-wise Summary")
    st.dataframe(zone_stats, use_container_width=True)

    # Station-wise drill-down (for stations only)
    station_assets = filtered_assets[filtered_assets["type"] == "Station"]
    st.subheader("Station-wise Details")
    st.dataframe(station_assets[[
        "asset_name", "line", "zone", "health_score", "cyber_risk_score",
        "vulnerability_count", "patch_compliance", "criticality"
    ]].sort_values("cyber_risk_score", ascending=False), use_container_width=True)

    # Heatmap of risk by zone and line
    pivot = filtered_assets.pivot_table(index="zone", columns="line", values="cyber_risk_score", aggfunc="mean").fillna(0)
    fig_heatmap = px.imshow(pivot, text_auto=True, aspect="auto", title="Average Cyber Risk Score (Zone × Line)")
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------------------
# Tab 5: SIEM Events & Alerts
# ---------------------------
with tab5:
    st.subheader("Security Information & Event Management (SIEM)")

    # Filter events by severity
    events_filtered = st.session_state.events_df[
        st.session_state.events_df["timestamp"] > datetime.now() - timedelta(hours=24)
    ]
    severity_filter_events = st.multiselect(
        "Filter by Severity", options=events_filtered["severity"].unique(), default=events_filtered["severity"].unique()
    )
    events_filtered = events_filtered[events_filtered["severity"].isin(severity_filter_events)]

    # Event timeline
    events_filtered["date_hour"] = events_filtered["timestamp"].dt.floor("H")
    hourly_counts = events_filtered.groupby(["date_hour", "severity"]).size().reset_index(name="count")
    fig_timeline = px.line(hourly_counts, x="date_hour", y="count", color="severity", title="Event Timeline (Last 24h)")
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Events table
    st.dataframe(events_filtered.sort_values("timestamp", ascending=False), use_container_width=True, height=500)

    # Top event types
    event_type_counts = events_filtered["event_type"].value_counts().reset_index()
    event_type_counts.columns = ["Event Type", "Count"]
    fig_events = px.bar(event_type_counts.head(10), x="Event Type", y="Count", title="Top 10 Event Types")
    st.plotly_chart(fig_events, use_container_width=True)

# ---------------------------
# Tab 6: Compliance & Recommendations
# ---------------------------
with tab6:
    st.subheader("Compliance Dashboard & Recommended Actions")

    # Compliance metrics (mock)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("NIST CSF Alignment", "72%")
        st.metric("IEC 62443 Compliance", "65%")
        st.metric("Patch Compliance Target (90%)", f"{filtered_assets['patch_compliance'].mean():.1f}%")
    with col2:
        st.metric("Incident Response Readiness", "68%")
        st.metric("Asset Inventory Completeness", "95%")
        st.metric("Security Awareness Training", "82%")

    # Recommendations based on data
    st.subheader("Actionable Recommendations")
    high_risk_assets = filtered_assets[filtered_assets["cyber_risk_score"] > 70]
    if not high_risk_assets.empty:
        st.warning(f"🔴 {len(high_risk_assets)} assets have high cyber risk. Prioritize remediation.")
        st.write("Assets:", high_risk_assets["asset_name"].tolist())

    low_patch = filtered_assets[filtered_assets["patch_compliance"] < 70]
    if not low_patch.empty:
        st.warning(f"🛡️ {len(low_patch)} assets have patch compliance below 70%. Schedule patching.")
        st.write("Assets:", low_patch["asset_name"].tolist())

    critical_vulns = st.session_state.vulns_df[st.session_state.vulns_df["severity"] == "Critical"]
    if not critical_vulns.empty:
        st.error(f"💣 {len(critical_vulns)} critical vulnerabilities detected across assets. Immediate action required.")
        st.dataframe(critical_vulns[["asset_name", "cve_id", "description"]])

    # General recommendations
    st.markdown("""
    ### General Recommendations
    - Implement network segmentation to isolate critical OT assets.
    - Conduct regular vulnerability scans and penetration testing.
    - Enhance SIEM correlation rules for early detection of anomalies.
    - Establish a 24/7 security operations center (SOC) for OT.
    - Perform regular tabletop exercises for incident response.
    """)

# Footer
st.markdown("---")
st.caption("Data refreshes dynamically. © Deloitte & Namma Metro – Confidential. Simulated for demonstration purposes.")