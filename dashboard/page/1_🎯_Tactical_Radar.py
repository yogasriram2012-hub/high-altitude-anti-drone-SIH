import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Layer 1: Tactical Radar", page_icon="🎯", layout="wide")
st.title("🎯 Layer 1: Tactical Radar & Threat HUD")

st.sidebar.subheader("Layer 1 Controls")
range_m = st.sidebar.slider("Target Range (m)", 10.0, 500.0, 130.0, 5.0)
pan_deg = st.sidebar.slider("Gimbal Pan / Heading (°)", 0.0, 180.0, 80.0, 1.0)
tilt_deg = st.sidebar.slider("Gimbal Elevation / Tilt (°)", 60.0, 120.0, 95.0, 1.0)
hold_time = st.sidebar.slider("Lock Duration (s)", 0.0, 5.0, 3.2, 0.1)

# Logic checks
armed = range_m < 150.0
engaged = range_m < 300.0
neutralized = armed and engaged and (hold_time >= 3.0)

tab1, tab2, tab3 = st.tabs(["Sub-layer 1.1: Polar Threat Radar", "Sub-layer 1.2: 3D Topographic HUD", "Sub-layer 1.3: Engagement State Machine"])

with tab1:
    st.subheader("Sub-layer 1.1: Polar PPI Radar Sweep (0–500 m)")
    fig_radar = go.Figure()
    theta_grid = np.linspace(0, 360, 200)
    fig_radar.add_trace(go.Scatterpolar(r=[500]*200, theta=theta_grid, mode='lines', line=dict(color='rgba(0,255,170,0.4)', width=1), name='500m Patrol'))
    fig_radar.add_trace(go.Scatterpolar(r=[300]*200, theta=theta_grid, fill='toself', fillcolor='rgba(255,170,0,0.08)', line=dict(color='orange', width=1.5), name='300m Track'))
    fig_radar.add_trace(go.Scatterpolar(r=[150]*200, theta=theta_grid, fill='toself', fillcolor='rgba(255,34,51,0.18)', line=dict(color='red', width=2), name='150m Intercept'))
    
    blip_col = '#9900ff' if neutralized else ('#ff2233' if armed else ('#ffaa00' if engaged else '#00ffaa'))
    fig_radar.add_trace(go.Scatterpolar(
        r=[range_m], theta=[pan_deg], mode='markers+text',
        marker=dict(size=18, color=blip_col, symbol='cross'),
        text=[f"UAS [{range_m:.0f}m]"], textposition="top center", name="Target Blip"
    ))
    fig_radar.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(range=[0, 500]), angularaxis=dict(direction="clockwise", rotation=90)), height=480)
    st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    st.subheader("Sub-layer 1.2: 3D Topographic Intercept HUD")
    x = np.linspace(-2, 2, 40)
    y = np.linspace(-2, 2, 40)
    X, Y = np.meshgrid(x, y)
    Z = 4500 + 1400 * np.exp(-(X**2 + Y**2)/2.0)
    
    drone_x = (range_m / 500.0) * 160 * np.cos(np.radians(pan_deg))
    drone_y = (range_m / 500.0) * 160 * np.sin(np.radians(pan_deg))
    drone_z = 4500 + range_m * np.sin(np.radians(tilt_deg - 90)) + 400

    fig_hud = go.Figure()
    fig_hud.add_trace(go.Surface(z=Z, x=X*100, y=Y*100, colorscale='Earth', opacity=0.8, showscale=False))
    fig_hud.add_trace(go.Scatter3d(
        x=[0, drone_x], y=[0, drone_y], z=[4500, drone_z],
        mode='lines+markers', line=dict(color='yellow', width=4, dash='dash'),
        marker=dict(size=[6, 12], color=['#00ffaa', blip_col], symbol=['diamond', 'cross']),
        name="Target Trajectory"
    ))
    fig_hud.update_layout(template="plotly_dark", height=480, scene=dict(xaxis_title="East (m)", yaxis_title="North (m)", zaxis_title="Altitude (m)"))
    st.plotly_chart(fig_hud, use_container_width=True)

with tab3:
    st.subheader("Sub-layer 1.3: Engagement State Machine & Hardware Triggers")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Green LED (Pin 7)", "ON" if (not engaged and not armed) else "OFF")
    c2.metric("Red LED (Pin 8)", "ON" if engaged else "OFF")
    c3.metric("Buzzer (Pin 13)", "1800 Hz" if (armed and not neutralized) else "MUTED")
    c4.metric("LCD Line 1", "** NEUTRALIZED **" if neutralized else ("FIRE LOCK <150M" if armed else "TRACKING" if engaged else "PATROL"))

    if neutralized:
        st.success("🎯 ** TARGET NEUTRALIZED ** // TARGET DESTROYED — Buzzer Auto-Silenced")
    elif armed:
        st.error("🚨 INTERCEPT ENGAGED (<150 m) — Buzzer 1800 Hz Active (Counting down 3s)")
    elif engaged:
        st.warning("⚠️ TRACKING ACQUIRED (150 m – 300 m) — Red LED Active")
    else:
        st.info("🟢 PATROL STANDBY (≥300 m) — Radar Scanning")
