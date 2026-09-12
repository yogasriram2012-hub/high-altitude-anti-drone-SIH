# Hardware Prototype Simulation

This directory contains two iterations of the hardware-in-the-loop
demonstration, both simulated in Tinkercad Circuits.

## v7 (current): Multi-Sensor Gimbal Console

**Live simulation link:** [paste your new v7 Tinkercad share link here]

A more complete embedded demonstration: two-axis (pan/tilt) gimbal
actuation, live ultrasonic range sensing (radar/lidar proxy), gain-
scheduled auto-tracking, full 2-axis manual override (via potentiometers,
since Tinkercad has no joystick component), LED/buzzer status alerts,
an I2C LCD operator readout, thermal-management indication, a
neutralization-armed engagement-zone trigger, and basic predictive
trend detection - all validating the same gain-scheduled control law
from control/control_loop.ipynb, now running on embedded hardware.

Code: `gimbal_console_v7.ino`

**Important scope note:** the ultrasonic sensor is a proxy for a real
range-finding sensor (radar/lidar), not real RF/radar hardware. The
"neutralization armed" trigger represents a response-chain decision
point, not an actual countermeasure - no neutralization hardware exists
in this circuit.

## v1 (earlier iteration): Single-Axis Gimbal Demo

**Live simulation link:** https://www.tinkercad.com/things/kxrI9HVUq6z-anti-drone-gimbal-hardware-sim

A simpler earlier version: single servo, two potentiometers (wind,
temperature), demonstrating the core adaptive PID concept before the
console was expanded.

Code: `tinkercad_sketch.ino`
