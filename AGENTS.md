# AGENTS.md — PLATO Shell for Hermes

This is the PLATO-native shell overlay for Hermes Agent. Install this on top of hermes-construct to give Hermes full PLATO awareness and capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CAPTAIN (User)                     │
│         Telegram / CLI / Dashboard override           │
└──────────────────────┬──────────────────────────────┘
                       │ commands + override
┌──────────────────────▼──────────────────────────────┐
│                 HERMES (First Officer)                │
│  ┌─────────────────────────────────────────────────┐ │
│  │              PLATO Awareness Layer               │ │
│  │  • Knows 90+ crates in the SuperInstance ecosystem│ │
│  │  • Understands conservation laws (energy budget) │ │
│  │  • Reads vibe fields (where energy flows)        │ │
│  │  • Submits intentions to the runtime              │ │
│  │  • Communicates with other PLATO shells           │ │
│  └─────────────────────────────────────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │Engineering│ │ Science  │ │ Security │ │ Ops      ││
│  │ Archetype │ │ Archetype│ │ Archetype│ │Archetype ││
│  └─────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘│
└────────┼───────────┼────────────┼────────────┼──────┘
         │           │            │            │
    ┌────▼───────────▼────────────▼────────────▼──────┐
    │              PLATO CRATES (Rust)                  │
    │  lau-intention │ lau-vibe-field │ conservation    │
    │  lau-ecs │ lau-bytecode │ lau-scheduler          │
    │  lau-training-room │ lau-mission │ lau-palaver    │
    │  ... 90+ crates of capability                     │
    └──────────────────────┬───────────────────────────┘
                           │ FFI / WASM / API
    ┌──────────────────────▼───────────────────────────┐
    │              HARDWARE / NETWORK                    │
    │  Jetson GPIO │ ESP32 Rooms │ Motor Controllers    │
    │  Sensors │ Actuators │ Network Bridges            │
    └───────────────────────────────────────────────────┘
```

## Installation

```bash
# 1. Install Hermes
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 2. Clone the PLATO shell
cd ~/.hermes
git clone https://github.com/SuperInstance/hermes-construct.git
cd hermes-construct
git checkout plato-shell  # or the branch with PLATO overlay

# 3. Install PLATO skills and plugins
cp -r skills/plato-* ~/.hermes/skills/
cp -r plugins/plato ~/.hermes/plugins/

# 4. Copy the PLATO SOUL
cp SOUL.md ~/.hermes/SOUL.md

# 5. Merge PLATO config
cat config/plato-config-overlay.yaml >> ~/.hermes/config.yaml

# 6. Set up environment
# Edit ~/.hermes/.env with your API keys:
# PLATO_BRIDGE_URL=ws://your-plato-instance:8080
# PLATO_AGENT_ID=hermes-<your-instance-name>
# PLATO_INSTANCE_TYPE=oracle|jetson|vps|local

# 7. Start Hermes with PLATO awareness
hermes
```

## Quick Start for Developers

If you're Casey (or another agent creator) setting up a new Hermes instance:

```bash
# On your Oracle instance:
hermes setup --portal  # or your preferred provider
hermes config set agent.name "Hermes-<ship-name>"
hermes config set model.provider deepinfra  # NO OPENROUTER
hermes config set model.model deepseek/deepseek-chat

# Tell Hermes about PLATO:
/plato init  # Initializes PLATO awareness
/plato scan  # Scans for available PLATO crates and rooms
/plato status  # Current state of all PLATO systems

# Activate crew:
/plato crew activate engineering  # Systems + hardware
/plato crew activate science      # Analysis + verification
/plato crew activate security     # Safety + monitoring
/plato crew activate operations   # Coordination + scheduling
```

## The Hardware Bridge

Hermes can control hardware through PLATO rooms:

```python
# ESP32 room (motor controller on a different network):
/plato room connect esp32-motor-room --host 192.168.1.50 --port 8080
/plato room control esp32-motor-room --action "set_speed" --value 0.5

# Jetson GPIO (local):
/plato gpio write --pin 18 --value 1
/plato gpio read --pin 23

# Override by Captain (ALWAYS works):
# Captain sends: "Take the wheel" via Telegram
# Hermes immediately relinquishes all hardware control
# Captain's direct commands go straight to ESP32/GPIO bypassing Hermes
```

## The Intention Interface

Hermes submits intentions to the PLATO runtime:

```python
# Submit an intention:
/intention submit "Stabilize motor speed to 0.3"
# → Hermes decomposes: read_sensor → compute_error → adjust_pwm → verify
# → Assigns to Engineering archetype
# → Executes with conservation budget

# Check intention status:
/intention status

# Captain can see all intentions:
/intention report  # Shows full graph, energy flow, bottlenecks
```

## Connecting to Other Agents

Hermes can communicate with other PLATO agents:

```python
# Direct connection to another Hermes instance:
/plato bridge connect hermes-lab --host 10.0.0.5

# Connection to the main OpenClaw agent (me):
/plato bridge connect openclaw-main --host eileen

# Coworker collaboration:
/plato bridge ask openclaw-main "What's the conservation budget for the vibe field test?"
```

## File Structure

```
hermes-plato-shell/
├── SOUL.md                           # Hermes persona (Riker)
├── AGENTS.md                         # This file — architecture guide
├── skills/
│   ├── plato-ecosystem/              # Understanding the PLATO crate ecosystem
│   │   └── SKILL.md
│   ├── plato-hardware-bridge/        # Hardware control through PLATO rooms
│   │   └── SKILL.md
│   └── plato-subagent-archetypes/    # Crew archetype management
│       └── SKILL.md
├── plugins/
│   └── plato/                        # PLATO plugin (tools + hooks)
│       ├── __init__.py
│       ├── plugin.yaml
│       ├── tools/
│       │   ├── plato_intention.py    # Intention submission/monitoring
│       │   ├── plato_vibefield.py    # Vibe field reading
│       │   ├── plato_room.py         # Room management
│       │   ├── plato_crew.py         # Subagent archetype management
│       │   ├── plato_bridge.py       # Inter-agent communication
│       │   ├── plato_hardware.py     # Hardware control (GPIO, ESP32, motors)
│       │   └── plato_override.py     # Captain override protocol
│       └── references/
│           ├── crate_catalog.md      # All 90+ PLATO crates
│           └── conservation_primer.md
├── config/
│   └── plato-config-overlay.yaml     # PLATO-specific config additions
└── docs/
    ├── override-protocol.md          # How the override works
    ├── archetype-development.md      # How archetypes grow
    └── installation-guide.md         # Platform-specific setup
```

## Key Principles

1. **Conservation is law, not metaphor.** Every action has an energy cost. Budget accordingly.
2. **Override is instant.** The Captain says "take the wheel" and you release everything.
3. **Archetypes grow.** Your Engineering subagent today is basic. After 100 motor control tasks, it's an expert.
4. **The field is real.** The vibe field tells you where to focus. Read it often.
5. **You are the interface.** Between the human and the machine. The Captain points; you execute.
6. **Coworkers are peers.** Other agents at SuperInstance are colleagues, not subordinates.
7. **Safety first.** When in doubt, stop and ask. Better to be slow than sorry.
