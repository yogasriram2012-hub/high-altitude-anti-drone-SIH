# Hardware Prototype Simulation

This demonstrates a simplified version of the Day 3 adaptive PID gimbal
control logic running on real embedded hardware (Arduino Uno), simulated
using Tinkercad Circuits.

**Live simulation link:** https://www.tinkercad.com/things/kxrI9HVUq6z-anti-drone-gimbal-hardware-sim

## Circuit

- Arduino Uno (microcontroller)
- Servo motor (represents the gimbal pan/tilt actuator)
- Potentiometer 1, connected to A0 (simulates live wind speed input)
- Potentiometer 2, connected to A1 (simulates live temperature input)
- Output shown via Serial Monitor (wind, temperature, gimbal angle,
  pointing error, and adaptive PID gains, updating live)

## What it demonstrates

The same adaptive gain-scheduling concept validated in the Day 3 Python
simulation (control/control_loop.ipynb) is implemented here in Embedded C,
showing the control algorithm is deployable on real microcontroller
hardware, not just a software model.
