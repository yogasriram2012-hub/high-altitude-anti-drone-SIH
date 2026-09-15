import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="C-UAS GCS // SIH 26050", page_icon="🏔️", layout="wide")

st.title("🏔️ High-Altitude Anti-Drone Defense System (C-UAS)")
st.caption("Hardware-in-the-Loop Ground Control Station // SIH Problem Statement 26050")

st.markdown("""
### Tactical 3×3 Mission Control Architecture
* **Layer 1: Tactical Radar & Threat HUD**
  * Sub-layer 1.1: Polar Threat Radar (PPI Sweep 0–500m)
  * Sub-layer 1.2: 3D Topographic HUD (Everest Theater)
  * Sub-layer 1.3: Engagement State Machine & Neutralization
* **Layer 2: High-Altitude RF Link & Thermal Management**
  * Sub-layer 2.1: Friis Path-Loss & Received Power Model
  * Sub-layer 2.2: Dynamic Thermal Noise Floor & SNR Margin
  * Sub-layer 2.3: Closed-Loop Proportional PWM Heater (Pin D5)
* **Layer 3: 2-Axis Gimbal Control & Disturbance Analytics**
  * Sub-layer 3.1: Transient Tracking Error Response (Pan/Tilt)
  * Sub-layer 3.2: 3D Gain-Scheduling Dynamic Surfaces
  * Sub-layer 3.3: Gimbal Orientation & Servo Health Telemetry
""")

st.write("---")
st.subheader("Global Mountain Theater (Mount Everest Sector)")

x = np.linspace(-3, 3, 50)
y = np.linspace(-3, 3, 50)
X, Y = np.meshgrid(x, y)
Z = 4500 + 1900 * np.exp(-(X**2 + Y**2)/2.8)

fig = go.Figure(data=[go.Surface(z=Z, x=X*100, y=Y*100, colorscale='Earth', opacity=0.85, showscale=False)])
fig.add_trace(go.Scatter3d(
    x=[0, 110], y=[0, 95], z=[4500, 5600],
    mode='lines+markers',
    line=dict(color='#ff2233', width=5, dash='dash'),
    marker=dict(size=[8, 14], color=['#00ffaa', '#ff2233'], symbol=['diamond', 'cross']),
    name="Hostile Track"
))
fig.update_layout(template="plotly_dark", height=420, scene=dict(xaxis_title="East (m)", yaxis_title="North (m)", zaxis_title="Altitude (m)"))
st.plotly_chart(fig, use_container_width=True)
