"""
Home / Overview Page
High Altitude Anti-Drone System Simulation (SIH Problem Statement 26050)

This is now a genuine multi-page Streamlit app (not one long scrolling
page). Use the sidebar to navigate between:
  - Environment & RF   : atmospheric model, RF/SNR link budget
  - Control & Tracking : adaptive PID vs baseline, Kalman filter tracking
  - Health Monitor     : aggregated system health score, trend detection

Shared sliders (altitude, wind) persist across pages via session state.
"""

import streamlit as st

st.set_page_config(page_title="C-UAS Simulation Suite", layout="wide", page_icon="🛰️")

st.title("High Altitude Anti-Drone System — Simulation Suite")
st.caption("SIH Problem Statement 26050 (DRDO) — Environmental Compensation Subsystem")

st.markdown("""
Use the sidebar to navigate between pages. Altitude and wind settings are shared
across all pages, so a scenario you set on one page carries through to the others.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Environment & RF")
    st.write("ISA atmospheric model, wind-gust disturbance, and RF/SNR link-budget analysis "
             "for drone signal detection.")
with col2:
    st.subheader("Control & Tracking")
    st.write("Gain-scheduled adaptive PID control vs. fixed-gain baseline, and Kalman-filtered "
             "drone tracking vs. raw noisy measurement.")
with col3:
    st.subheader("Health Monitor")
    st.write("Aggregated system health score combining environmental stress, pointing error, "
             "and RF link quality, with basic degradation-trend detection.")

st.divider()
st.subheader("Project scope note")
st.markdown("""
This suite demonstrates the **environmental compensation and detection-support subsystem**
of the anti-drone problem statement — gain-scheduled control, state estimation, and RF link
analysis, all grounded in real physics (ISA atmosphere, Friis path-loss equation) rather than
arbitrary numbers. It does **not** include RF jamming/neutralization hardware, ruggedized
mechanical design, or field-validated components — those are scoped as next-phase work.

A companion hardware-in-the-loop prototype (Arduino Uno + Tinkercad) validates the same
control law on embedded hardware. See the project README for details and links.
""")
