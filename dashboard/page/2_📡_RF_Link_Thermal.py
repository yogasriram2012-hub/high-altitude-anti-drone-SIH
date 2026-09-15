import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Layer 2: RF & Thermal", page_icon="📡", layout="wide")
st.title("📡 Layer 2: High-Altitude RF Link & Thermal Management")

st.sidebar.subheader("Layer 2 Controls")
temp_c = st.sidebar.slider("Ambient Temp (°C)", -20.0, 15.0, -12.0, 0.5)
wind_speed = st.sidebar.slider("Wind Velocity (km/h)", 5.0, 65.0, 35.0, 1.0)
dist_m = st.sidebar.slider("Link Distance (m)", 10.0, 500.0, 150.0, 5.0)

# Math
dist_km = max(dist_m, 1.0) / 1000.0
fspl = 20.0 * np.log10(dist_km) + (20.0 * np.log10(2400.0) + 32.44)
temp_k = temp_c + 273.15
atm_loss = 0.05 * np.clip((1.0 - (0.0065 * 4500.0 / 288.15)) ** 5.255 * (288.15 / temp_k), 0.2, 1.0) * dist_km
rx_power = 20.0 + 14.0 + 2.0 - fspl - atm_loss - 2.0
noise_floor = 10.0 * np.log10(1.380649e-23 * max(150.0, temp_k) * 20.0e6) + 30.0 + 6.0
snr = rx_power - noise_floor
heater_pwm = int(np.interp(temp_c, [-20.0, -5.0], [255, 60])) if temp_c < -5.0 else 0

tab1, tab2, tab3 = st.tabs(["Sub-layer 2.1: Friis Link Budget", "Sub-layer 2.2: Dynamic Noise Floor", "Sub-layer 2.3: Closed-Loop Thermal PWM"])

with tab1:
    st.subheader("Sub-layer 2.1: Friis Path-Loss & Signal Power Curve")
    ranges = np.linspace(10, 500, 100)
    rx_curve = 20.0 + 14.0 + 2.0 - (20.0 * np.log10(ranges / 1000.0) + 100.044) - 2.0
    fig_f = go.Figure()
    fig_f.add_trace(go.Scatter(x=ranges, y=rx_curve, mode='lines', line=dict(color='#00e5ff', width=2), name="Rx Power (dBm)"))
    fig_f.add_trace(go.Scatter(x=[dist_m], y=[rx_power], mode='markers', marker=dict(size=12, color='yellow'), name="Live Operating Point"))
    fig_f.update_layout(template="plotly_dark", xaxis_title="Distance (m)", yaxis_title="Received Power (dBm)", height=420)
    st.plotly_chart(fig_f, use_container_width=True)

with tab2:
    st.subheader("Sub-layer 2.2: Real-Time Dynamic Noise Floor & Link Margin")
    st.metric("Link SNR Margin", f"{snr:.1f} dB", delta="Locked" if snr >= 10.0 else "Weak")
    st.metric("Thermal Noise Floor (kTB + NF)", f"{noise_floor:.2f} dBm")
    
    t_sweep = np.linspace(-20, 15, 50)
    nf_sweep = [10.0 * np.log10(1.380649e-23 * (t + 273.15) * 20.0e6) + 36.0 for t in t_sweep]
    fig_nf = go.Figure(data=[go.Scatter(x=t_sweep, y=nf_sweep, mode='lines', line=dict(color='#ff3366', width=2))])
    fig_nf.update_layout(template="plotly_dark", xaxis_title="Temperature (°C)", yaxis_title="Noise Floor (dBm)", height=350)
    st.plotly_chart(fig_nf, use_container_width=True)

with tab3:
    st.subheader("Sub-layer 2.3: Proportional PWM Heater Response (Pin D5)")
    st.metric("Heater PWM Output", f"{heater_pwm} / 255", delta="Active" if heater_pwm > 0 else "Off")
    t_range = np.linspace(-25, 10, 100)
    pwm_curve = [int(np.interp(t, [-20.0, -5.0], [255, 60])) if t < -5.0 else 0 for t in t_range]
    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(x=t_range, y=pwm_curve, fill='tozeroy', line=dict(color='#ff5533', width=2), name="PWM Intensity"))
    fig_h.add_vline(x=-5.0, line_dash="dash", line_color="yellow", annotation_text="Heater Trigger (-5°C)")
    fig_h.update_layout(template="plotly_dark", xaxis_title="Ambient Temperature (°C)", yaxis_title="PWM Duty Cycle (0–255)", height=400)
    st.plotly_chart(fig_h, use_container_width=True)
