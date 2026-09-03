# High Altitude Performance Optimization and Robust Design of Anti-Drone System (Simulation)

Problem Statement ID: 26050
Organization: DRDO, Department of Defence Production / IDEX
Category: Hardware
Theme: Robotics and Drones

## Problem Summary

Anti-drone systems degrade in high-altitude environments due to extreme cold, low pressure, reduced air density, dust, and high wind. These conditions affect mechanical, electrical, RF, and electro-optical subsystems. This project simulates that degradation and demonstrates compensation mechanisms for precision pointing, tracking, and detection performance.

## Scope

This simulation covers three modules only.

Environmental Model: Models how altitude affects temperature, pressure, air density, and wind, to generate realistic disturbance inputs for the other modules.

Gimbal Pointing and Control Compensation: Simulates a two-axis gimbal PID controller under environmental disturbance, and compares it against an adaptive gain-scheduled controller that compensates for the disturbance, measured through reduced pointing error in microradians.

Drone Detection and Tracking: Simulates a drone flight path, adds environment-linked sensor noise, tracks the drone using a Kalman filter, and detects it using a YOLOv8 model under degraded visibility conditions.

## Out of Scope

Mechanical or hardware prototype. RF jamming or neutralization hardware. Real embedded deployment, since Wokwi hardware-in-loop is an optional bonus and not a core deliverable. Multi-drone swarm tracking. Real-time video feed integration, since simulated and dataset images are used instead.

## Tech Stack

Code and simulation: Google Colab. Version control: GitHub. Control loop: Python with numpy. Tracking: FilterPy for Kalman filtering. Detection: YOLOv8 through ultralytics, using a Kaggle drone dataset. Reference data: International Standard Atmosphere formulas. Dashboard: Streamlit, deployed on Streamlit Community Cloud. Diagrams: draw.io. Presentation: Google Slides or Canva.

## Folder Structure

env_model holds the ISA and wind disturbance model. control holds the PID and adaptive gain-scheduled gimbal controller. tracking holds the Kalman filter drone tracking simulation. detection holds the YOLOv8 detection model under degraded visibility. dashboard holds the Streamlit integration app.

## Seven Day Plan

Day 1: Scope, repo, Colab setup, ISA research.
Day 2: Environmental model covering temperature, pressure, density, and wind versus altitude.
Day 3: Gimbal PID control loop, baseline versus adaptive.
Day 4: Kalman filter tracking under environmental noise.
Day 5: YOLOv8 drone detection under degraded visibility.
Day 6: Streamlit integration dashboard, deployed live.
Day 7: Demo video, presentation, final polish, submission.

## How to Run

Clone this repository. Open the notebooks in Google Colab, linked through GitHub. Install dependencies using pip install numpy matplotlib filterpy ultralytics streamlit. Run the dashboard locally using streamlit run app.py, or use the deployed link once it is added after Day 6.
