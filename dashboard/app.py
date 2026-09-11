"""
Day 7 - Streamlit Integration Dashboard
High Altitude Anti-Drone System Simulation (SIH Problem Statement 26050)

Combines the environmental model (Day 2), gimbal control (Day 3), and
Kalman filter tracking (Day 4) into one interactive dashboard. Sliders
for altitude, temperature, and wind drive all modules live.

To run locally: streamlit run app.py
To deploy: push this file (plus requirements.txt) to GitHub, then
deploy via share.streamlit.io pointing at this file.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag

st.set_page_config(page_title="High Altitude Anti-Drone System Simulation", layout="wide")

# ---------------------------------------------------------
# Environmental Model (Day 2)
# ---------------------------------------------------------
T0 = 288.15
L = 0.0065
P0 = 101325.0
R = 287.05
G = 9.80665

def isa_temperature(altitude_m):
    return T0 - L * altitude_m

def isa_pressure(altitude_m):
    temp = isa_temperature(altitude_m)
    return P0 * (temp / T0) ** (G / (R * L))

def isa_density(altitude_m):
    pressure = isa_pressure(altitude_m)
    temp = isa_temperature(altitude_m)
    return pressure / (R * temp)


# ---------------------------------------------------------
# Gimbal Control Model (Day 3)
# ---------------------------------------------------------
class GimbalAxis:
    def __init__(self, inertia=0.02):
        self.inertia = inertia
        self.angle = 0.0
        self.angular_velocity = 0.0

    def friction_coefficient(self, temp_c):
        base_friction = 0.05
        cold_penalty = max(0, (0 - temp_c)) * 0.004
        return base_friction + cold_penalty

    def step(self, motor_torque, disturbance_torque, temp_c, dt):
        friction = self.friction_coefficient(temp_c) * self.angular_velocity
        net_torque = motor_torque - friction - disturbance_torque
        angular_accel = net_torque / self.inertia
        self.angular_velocity += angular_accel * dt
        self.angle += self.angular_velocity * dt
        return self.angle


class PIDController:
    def __init__(self, kp, ki, kd, d_filter_alpha=0.2):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.filtered_derivative = 0.0
        self.alpha = d_filter_alpha

    def compute(self, error, dt):
        self.integral += error * dt
        self.integral = np.clip(self.integral, -50, 50)
        raw_derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.filtered_derivative = (self.alpha * raw_derivative +
                                     (1 - self.alpha) * self.filtered_derivative)
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * self.filtered_derivative


def gain_schedule(temp_c, wind_speed, base_kp=8.0, base_ki=0.5, base_kd=1.2, adaptive=True):
    if not adaptive:
        return base_kp, base_ki, base_kd
    cold_factor = max(0, (0 - temp_c)) / 40.0
    wind_factor = wind_speed / 25.0
    severity = np.clip(cold_factor * 0.5 + wind_factor * 0.5, 0, 1)
    kp = base_kp * (1 + 0.35 * severity)
    ki = base_ki * (1 - 0.2 * severity)
    kd = base_kd * (1 + 0.25 * severity)
    return kp, ki, kd


def wind_gust_model(time_s, base_wind_speed, gust_amplitude=4.0, gust_freq=0.2, noise_std=1.0, seed=42):
    rng = np.random.default_rng(seed)
    sinusoidal_gust = gust_amplitude * np.sin(2 * np.pi * gust_freq * time_s)
    turbulence = rng.normal(0, noise_std, size=len(time_s))
    return np.clip(base_wind_speed + sinusoidal_gust + turbulence, 0, None)


def wind_disturbance_series(wind_profile, drag_coefficient=0.0003):
    smoothed = np.convolve(wind_profile, np.ones(15) / 15, mode='same')
    deviation = wind_profile - smoothed
    return drag_coefficient * wind_profile * deviation


def run_control_simulation(target_deg, altitude_m, wind_base_speed, adaptive, duration_s=20, dt=0.02):
    target_rad = np.radians(target_deg)
    n_steps = int(duration_s / dt)
    time = np.linspace(0, duration_s, n_steps)
    temp_c = isa_temperature(altitude_m) - 273.15
    wind_profile = wind_gust_model(time, wind_base_speed)
    disturbance_series = wind_disturbance_series(wind_profile)

    axis = GimbalAxis()
    kp, ki, kd = gain_schedule(temp_c, wind_base_speed, adaptive=adaptive)
    pid = PIDController(kp, ki, kd)
    error_arr = np.zeros(n_steps)

    for i in range(n_steps):
        if adaptive:
            pid.kp, pid.ki, pid.kd = gain_schedule(temp_c, wind_profile[i])
        error = target_rad - axis.angle
        torque = pid.compute(error, dt)
        axis.step(torque, disturbance_series[i], temp_c, dt)
        error_arr[i] = error

    return time, error_arr * 1e6, temp_c  # microradians


# ---------------------------------------------------------
# Kalman Tracking Model (Day 4)
# ---------------------------------------------------------
def sensor_noise_std(altitude_m, wind_speed):
    temp_c = isa_temperature(altitude_m) - 273.15
    cold_factor = max(0, (0 - temp_c)) / 40.0
    wind_factor = wind_speed / 25.0
    severity = np.clip(cold_factor * 0.5 + wind_factor * 0.5, 0, 1)
    return 3.0 + severity * 25.0


def generate_drone_path(duration_s=20, dt=0.1):
    time = np.arange(0, duration_s, dt)
    x = 200 * np.sin(0.3 * time)
    y = 100 * np.sin(0.6 * time)
    return time, x, y


def run_tracking_simulation(altitude_m, wind_speed, duration_s=20, dt=0.1):
    time, true_x, true_y = generate_drone_path(duration_s, dt)
    noise_std = sensor_noise_std(altitude_m, wind_speed)
    rng = np.random.default_rng(7)
    noisy_x = true_x + rng.normal(0, noise_std, size=len(true_x))
    noisy_y = true_y + rng.normal(0, noise_std, size=len(true_y))

    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.F = np.array([[1, dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, dt], [0, 0, 0, 1]])
    kf.H = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])
    kf.R = np.eye(2) * (noise_std ** 2)
    q_axis = Q_discrete_white_noise(dim=2, dt=dt, var=800.0)
    kf.Q = block_diag(q_axis, q_axis)
    kf.x = np.array([noisy_x[0], 0., noisy_y[0], 0.])
    kf.P = np.eye(4) * 20.0

    filtered_x, filtered_y = [], []
    for zx, zy in zip(noisy_x, noisy_y):
        kf.predict()
        kf.update(np.array([zx, zy]))
        filtered_x.append(kf.x[0])
        filtered_y.append(kf.x[2])

    filtered_x, filtered_y = np.array(filtered_x), np.array(filtered_y)
    raw_error = np.sqrt((noisy_x - true_x) ** 2 + (noisy_y - true_y) ** 2)
    filtered_error = np.sqrt((filtered_x - true_x) ** 2 + (filtered_y - true_y) ** 2)

    return true_x, true_y, noisy_x, noisy_y, filtered_x, filtered_y, raw_error, filtered_error, noise_std


# ---------------------------------------------------------
# Dashboard Layout
# ---------------------------------------------------------
st.title("High Altitude Anti-Drone System — Simulation Dashboard")
st.caption("SIH Problem Statement 26050 (DRDO) — adjust conditions to see how the system responds")

col1, col2, col3 = st.columns(3)
with col1:
    altitude = st.slider("Altitude (m)", 0, 6000, 4500, step=100)
with col2:
    wind = st.slider("Wind speed (m/s)", 0, 25, 12, step=1)
with col3:
    st.metric("Temperature at altitude", f"{isa_temperature(altitude) - 273.15:.1f} °C")

density = isa_density(altitude)
st.metric("Air density", f"{density:.3f} kg/m³")

st.divider()

# --- Control section ---
st.subheader("Gimbal Pointing Control: Baseline vs Adaptive")
time_c, err_baseline, temp_c = run_control_simulation(5, altitude, wind, adaptive=False)
_, err_adaptive, _ = run_control_simulation(5, altitude, wind, adaptive=True)

settle_idx = int(2 / 0.02)
mean_baseline = np.mean(np.abs(err_baseline[settle_idx:]))
mean_adaptive = np.mean(np.abs(err_adaptive[settle_idx:]))

c1, c2 = st.columns(2)
c1.metric("Baseline PID mean error", f"{mean_baseline:.1f} µrad")
c2.metric("Adaptive PID mean error", f"{mean_adaptive:.1f} µrad",
          delta=f"{mean_adaptive - mean_baseline:.1f} µrad", delta_color="inverse")

fig1, ax1 = plt.subplots(figsize=(10, 3.5))
ax1.plot(time_c, err_baseline, label="Baseline PID", color="tab:red", alpha=0.8)
ax1.plot(time_c, err_adaptive, label="Adaptive PID", color="tab:green", alpha=0.8)
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Pointing Error (µrad)")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

st.divider()

# --- Tracking section ---
st.subheader("Drone Tracking: Raw Measurement vs Kalman Filtered")
(true_x, true_y, noisy_x, noisy_y, filtered_x, filtered_y,
 raw_error, filtered_error, noise_std) = run_tracking_simulation(altitude, wind)

settle_idx_t = int(1.0 / 0.1)
mean_raw = np.mean(raw_error[settle_idx_t:])
mean_filtered = np.mean(filtered_error[settle_idx_t:])

c3, c4 = st.columns(2)
c3.metric("Raw measurement mean error", f"{mean_raw:.1f} m")
c4.metric("Kalman filtered mean error", f"{mean_filtered:.1f} m",
          delta=f"{mean_filtered - mean_raw:.1f} m", delta_color="inverse")

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(true_x, true_y, label="True path", color="black", linewidth=2)
ax2.scatter(noisy_x, noisy_y, label="Noisy measurements", color="tab:red", s=8, alpha=0.4)
ax2.plot(filtered_x, filtered_y, label="Kalman filtered", color="tab:green", linewidth=2)
ax2.set_xlabel("X position (m)")
ax2.set_ylabel("Y position (m)")
ax2.legend()
ax2.grid(True)
ax2.axis("equal")
st.pyplot(fig2)

st.divider()
st.caption("Environmental model (Day 2), adaptive control (Day 3), and Kalman tracking (Day 4) "
           "all respond live to the sliders above. Detection results (Day 5, YOLOv8) and the "
           "hardware prototype (Day 6, Tinkercad) are presented separately in the project PPT/video.")


