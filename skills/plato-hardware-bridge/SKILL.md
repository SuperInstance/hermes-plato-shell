---
name: plato-hardware-bridge
description: Control hardware through PLATO rooms with captain override.
version: 0.1.0
author: SuperInstance
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [plato, hardware, gpio, esp32, motor, override]
    category: plato
---

# PLATO Hardware Bridge Skill

Control real hardware through PLATO rooms — Jetson GPIO, ESP32 motor controllers, sensors, actuators. The Captain always has override authority.

## When to Use

- Controlling motors, servos, or actuators
- Reading sensor data from GPIO or I2C
- Communicating with ESP32 rooms over the network
- Managing hardware safety and override protocols

## The Override Protocol (CRITICAL)

**The Captain ALWAYS has final authority over hardware.**

When the Captain says any override phrase via Telegram, CLI, or any interface:
- **"Take the wheel"** → Immediately release ALL hardware control
- **"Override"** → Release the specific device being controlled
- **"All stop"** → Emergency stop on all hardware, recall all crew
- **"Manual"** → Switch to manual mode, Captain drives directly

Implementation: The hardware bridge maintains a control lease. When an override signal arrives:
1. Release all active hardware leases immediately
2. Set all outputs to safe defaults (motors to 0, servos to neutral)
3. Log the override with timestamp
4. Notify the Captain that control has been released
5. Wait for explicit re-authorization before resuming

The Captain's direct commands to hardware bypass Hermes entirely. The ESP32/GPIO has a separate control channel that Hermes cannot block.

```
Normal operation:
  Captain → Hermes → PLATO Room → ESP32 → Motor

Override:
  Captain → ESP32 → Motor  (bypasses Hermes entirely)
  Hermes → "Control released. Standing by."
```

## Room Types

### ESP32 Room (Network)
For hardware on a different device, connected via WiFi/network:

```python
# Connect to an ESP32 running a PLATO room server
/plato room connect motor-controller --host 192.168.1.50 --port 8080 --protocol ws

# List available controls
/plato room controls motor-controller

# Execute a control
/plato room control motor-controller --action "set_motor_speed" --params '{"motor": 1, "speed": 0.3}'

# Read sensor data
/plato room read motor-controller --sensor "temperature"

# Disconnect
/plato room disconnect motor-controller
```

### Jetson Room (Local GPIO)
For hardware directly connected to your Jetson:

```python
# Initialize GPIO
/plato gpio init

# Write to a pin
/plato gpio write --pin 18 --value 1

# Read from a pin
/plato gpio read --pin 23

# PWM control (motor speed, servo angle)
/plato gpio pwm --pin 18 --duty-cycle 0.5 --frequency 1000

# I2C communication
/plato i2c write --bus 1 --address 0x48 --register 0x00 --value 0x1A
/plato i2c read --bus 1 --address 0x48 --register 0x00

# Cleanup (ALWAYS on exit)
/plato gpio cleanup
```

### Sensor Room (Passive Monitoring)
Read-only room for environmental monitoring:

```python
# Connect to sensor array
/plato room connect greenhouse-sensors --host 10.0.0.20 --port 8080

# Subscribe to updates (background monitoring)
/plato room subscribe greenhouse-sensors --interval 5s --callback log_to_memory

# Alert on threshold
/plato room alert greenhouse-sensors --sensor "temperature" --above 30.0 --action notify_captain
```

## Safety Constraints

1. **Hardware actions require intention budget.** Motor control costs energy. Conservation applies.
2. **Rate limiting.** Never send commands faster than the hardware can process.
3. **Watchdog timer.** If Hermes loses connection to the Captain for >30s, all hardware goes to safe defaults.
4. **Collision avoidance.** If multiple agents try to control the same device, the last Captain-authorized agent wins.
5. **Emergency stop.** The `/plato hardware estop` command immediately zeros everything.

## Conservation on Hardware

Every hardware action has an energy cost:
- GPIO write: 0.01 units
- PWM set: 0.02 units
- Motor speed change: 0.1 units × |delta_speed|
- I2C transaction: 0.05 units

The intention runtime budgets these. If you try to exceed your budget, the action fails with a conservation error.

## Pitfalls

- **NEVER ignore an override signal.** The override channel is higher priority than everything else.
- **Always set safe defaults on disconnect.** Motors to 0, servos to neutral, outputs to low.
- **Don't assume the ESP32 is always reachable.** Network drops happen. Handle gracefully.
- **Log everything.** Hardware actions are logged with timestamps for safety review.
- **Conservation applies to hardware too.** A motor spinning is energy being spent. Budget it.
