High Altitude Performance Optimization & Robust Design of Anti-Drone System (Simulation)

Problem Statement ID: 26050 Organization: DRDO — Department of Defence Production / IDEX Category: Hardware | Theme: Robotics and Drones

Problem Summary

Anti-drone systems degrade in high-altitude environments (extreme cold, low pressure, reduced air density, dust, high wind) due to changes in mechanical, electrical, RF, and electro-optical subsystem behavior. This project simulates that degradation and proposes/validates compensation mechanisms for precision pointing, tracking, and detection performance.

Scope

This simulation covers 3 modules only:

Environmental Model Goal: Model how altitude (temperature, pressure, air density, wind) changes with elevation, to drive realistic disturbance inputs for the other two modules.
Gimbal Pointing / Control Compensation Goal: Simulate a 2-axis gimbal PID controller under environmental disturbance, and show an adaptive/gain-scheduled version compensating for it (reduced pointing error in µrad).
Drone Detection & Tracking Goal: Simulate a drone flight path, add environment-linked sensor noise, track it with a Kalman filter, and detect it with a YOLOv8 model under degraded visibility conditions.
Out of Scope
Mechanical/hardware prototype
RF jamming / neutralization hardware
Real embedded deployment (Wokwi hardware-in-loop is optional bonus only, not a core deliverable)
Multi-drone swarm tracking
Real-time video feed integration (simulated/dataset images only)
Tech Stack
Function	Tool
Code + simulation	Google Colab
Version control	GitHub
Control loop	Python (numpy)
Tracking	FilterPy (Kalman filter)
Detection	YOLOv8 (ultralytics), Kaggle drone dataset
Reference data	ISA (International Standard Atmosphere) formulas
Dashboard	Streamlit + Streamlit Community Cloud
Diagrams	draw.io
Presentation	Google Slides / Canva
Folder Structure
/env_model      -> ISA + wind disturbance model
/control        -> PID and adaptive/gain-scheduled gimbal controller
/tracking       -> Kalman filter drone tracking sim
/detection      -> YOLOv8 detection under degraded visibility
/dashboard      -> Streamlit integration app
7-Day Plan Checklist
 Day 1 — Scope, repo, Colab setup, ISA research
 Day 2 — Environmental model (temp/pressure/density/wind vs altitude)
 Day 3 — Gimbal PID control loop (baseline vs adaptive)
 Day 4 — Kalman filter tracking under environmental noise
 Day 5 — YOLOv8 drone detection under degraded visibility
 Day 6 — Streamlit integration dashboard, deploy live
 Day 7 — Demo video, PPT, final polish, submit
How to Run
Clone this repo
Open notebooks in Google Colab (linked via GitHub)
Install dependencies: pip install numpy matplotlib filterpy ultralytics streamlit
Run dashboard/app.py locally with streamlit run app.py, or use the deployed link (added after Day 6)
