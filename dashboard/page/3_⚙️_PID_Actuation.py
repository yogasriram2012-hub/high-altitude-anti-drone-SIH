import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Layer 3: PID Diagnostics", page_icon="⚙️", layout="wide")
st.title("⚙️ Layer 3: 2-Axis Gimbal Control & Disturbance Analytics")

st.sidebar.subheader("Layer 3 Controls")
wind_k = st.sidebar.slider("Wind Velocity (km/h)", 5.0, 65.0, 30.0, 1.0)
temp_k = st.sidebar.slider("Temperature (°C)", -20.0, 15.0, -8.0, 1.0)

# Gains
severity = np.clip(max(0.0, -temp_k)/20.0 * 0.5 + (wind_k - 5.0)/60.0 * 0.5, 0.0, 1.0)
kp = 0.6 * (1.0 + 0.35 * severity)
ki = 0.02 * (1.0 - 0.20 * severity)
kd = 0.15 * (1.0 + 0.25 * severity)

tab1, tab2, tab3 = st.tabs(["Sub-layer 3.1: Pointing Error Strip Chart", "Sub-layer 3.2: 3D Gain-Scheduling Surface", "Sub-layer 3.3: Gimbal Orientation Telemetry"])

with tab1:
    st.subheader("Sub-layer 3.1: Transient Pan Tracking Error Response")
    t = np.linspace(0, 10, 250)
    noise = (wind_k / 65.0) * np.sin(3.5 * t) + np.random.normal(0, 0.1, 250)
    err = 2.4 * np.exp(-0.6 * t) * np.cos(4.0 * t) + noise * 0.3
    fig_err = go.Figure()
    fig_err.add_trace(go.Scatter(x=t, y=err, mode='lines', line=dict(color='#ff3366', width=2), name="ErrPan (°)"))
    fig_err.add_hline(y=0.5, line_dash="dot", line_color="#00ffaa", annotation_text="+0.5° Degraded")
    fig_err.add_hline(y=-0.5, line_dash="dot", line_color="#00ffaa", annotation_text="-0.5° Degraded")
    fig_err.update_layout(template="plotly_dark", xaxis_title="Time (s)", yaxis_title="Pointing Error (°)", height=420)
    st.plotly_chart(fig_err, use_container_width=True)

with tab2:
    st.subheader("Sub-layer 3.2: Dynamic 3D Gain-Scheduling Surface (Kp)")
    W_grid = np.linspace(5, 65, 25)
    T_grid = np.linspace(-20, 15, 25)
    W, T = np.meshgrid(W_grid, T_grid)
    Kp_surf = 0.6 * (1.0 + 0.35 * np.clip(np.clip(-T/20.0, 0, 1)*0.5 + ((W-5.0)/60.0)*0.5, 0, 1))
    fig_s = go.Figure(data=[go.Surface(z=Kp_surf, x=W, y=T, colorscale='Viridis', showscale=False)])
    fig_s.update_layout(template="plotly_dark", scene=dict(xaxis_title="Wind (km/h)", yaxis_title="Temp (°C)", zaxis_title="Scheduled Kp"), height=420)
    st.plotly_chart(fig_s, use_container_width=True)

with tab3:
    st.subheader("Sub-layer 3.3: Gimbal Orientation & Servo Health")
    c1, c2, c3 = st.columns(3)
    c1.metric("Scheduled Kp", f"{kp:.3f}")
    c2.metric("Scheduled Ki", f"{ki:.4f}")
    c3.metric("Scheduled Kd", f"{kd:.3f}")
    st.info("Dual servos operate on Pin D9 (Pan) and Pin D6 (Tilt) with active derivative filtering to eliminate kick.")
