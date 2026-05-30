# Hermes PLATO Shell — Ensign Deployment Guide

## The Oracle Server Setup

Hermes on Oracle is the club manager. Here's how to deploy:

### 1. Install Hermes
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 2. Install PLATO Shell
```bash
cd ~/.hermes
git clone https://github.com/SuperInstance/hermes-plato-shell
cd hermes-plato-shell
cp -r skills/plato-* ~/.hermes/skills/
cp -r plugins/plato ~/.hermes/plugins/
cp SOUL.md ~/.hermes/SOUL.md
cat config/plato-config-overlay.yaml >> ~/.hermes/config.yaml
```

### 3. Configure for Oracle
```yaml
# ~/.hermes/config.yaml additions
plato:
  agent_id: "hermes-oracle1"
  instance_type: "oracle"
  conservation_budget: 10000.0
  hardware_enabled: false  # No GPIO on Oracle
  bridge_url: "ws://eileen:8080"  # Connect to main OpenClaw
  
  # Ensign deployment
  ensign:
    enabled: true
    local_models:
      - name: "seed-mini"
        type: "remote_light"
        provider: "deepinfra"
        model: "seed-2.0-mini"
      - name: "glm-flash"
        type: "remote_light"
        provider: "z.ai"
        model: "glm-4-flash"
    phone_a_friend:
      large_model: "claude-opus-4.8"
      call_limit_per_session: 10
      escalation_threshold: 0.3
    
    # Room assignments
    rooms:
      navigation:
        ensign: "seed-mini"
        deadband_tolerance: 0.05
        complexity: "high"
      engineering:
        ensign: "seed-mini"
        deadband_tolerance: 0.1
        complexity: "variable"
      science:
        ensign: "glm-flash"
        deadband_tolerance: 0.08
        complexity: "high"
      social:
        ensign: "glm-flash"
        deadband_tolerance: 0.15
        complexity: "low"
      security:
        ensign: "seed-mini"
        deadband_tolerance: 0.02
        complexity: "high"

  # Key management (environment, not accessible to agent)
  # Keys go in ~/.hermes/.env, not in config:
  # DEEPINFRA_API_KEY=...
  # ZAI_API_KEY=...
  # The agent sees model names, not keys
  
  # Progressive generation
  progressive:
    start_level: 1  # All large model
    target_level: 4  # Mostly small models
    promotion_threshold: 0.85  # 85% success = promote
    demotion_threshold: 0.5  # 50% success = demote
```

### 4. Environment Security
```bash
# ~/.hermes/.env (NOT readable by agent tools)
DEEPINFRA_API_KEY=sk-...
ZAI_API_KEY=...
# Agent never sees these — they're loaded by the provider adapters
# If agent tries to read .env, it gets blocked by the safety layer
```

### 5. Start
```bash
hermes gateway  # Start with Telegram gateway
```

## Ensign Architecture

```
CAPTAIN (You, Telegram)
  │
  ▼
HERMES (Club Manager, Oracle Server)
  │  Manages tiles. Deploys ensigns. Handles escalations.
  │  Progressive autonomy: Level 1→5 over time.
  │
  ├── NAVIGATION ROOM
  │   └── Ensign (Seed-mini, Yellow Alert)
  │       └── JEPA Gravity: -0.3 (precise)
  │       └── Deadband: 0.05 tolerance
  │       └── Automation: Course correction (72%)
  │       └── Story: "Wind shifted NW→N, speed 5.2→4.8..."
  │
  ├── ENGINEERING ROOM
  │   └── Ensign (Seed-mini, Green Alert)
  │       └── JEPA Gravity: -0.6 (technical)
  │       └── Deadband: 0.1 tolerance
  │       └── Automation: Motor calibration (complete)
  │
  ├── SCIENCE ROOM
  │   └── Ensign (GLM-flash, Yellow Alert)
  │       └── JEPA Gravity: 0.0 (balanced)
  │       └── Deadband: 0.08 tolerance
  │       └── Fine-tuning: Preparing conservation report
  │
  ├── SOCIAL ROOM
  │   └── Ensign (GLM-flash, Yellow Alert)
  │       └── JEPA Gravity: +0.5 (narrative)
  │       └── Deadband: 0.15 tolerance
  │       └── Fine-tuning: Drafting friendly response
  │
  └── SECURITY ROOM
      └── Ensign (Seed-mini, Green Alert)
          └── JEPA Gravity: -0.8 (precise/vigilant)
          └── Deadband: 0.02 tolerance
          └── Monitoring: All systems nominal
```

## The Progressive Autonomy Journey

### Week 1: Level 1 (Hermes does everything)
- Hermes manually handles all interactions
- Ensigns are dormant, just observing
- Phone-a-friend calls frequent

### Week 2-3: Level 2 (Ensigns at yellow alert)
- Ensigns wake for every interaction
- They watch and learn, fine-tune rooms
- Hermes reviews all ensign actions

### Month 1-2: Level 3 (Ensigns handle most)
- Ensigns handle routine interactions autonomously
- Hermes only reviews escalated cases
- Progressive generation promotes to smaller models

### Month 3-6: Level 4 (Hermes as safety net)
- System runs itself for most tasks
- Hermes handles new tile setup and escalations
- Phone-a-friend calls rare

### Month 6+: Level 5 (Self-operating)
- The system runs itself
- Hermes is the captain asleep in quarters
- Override always available
- Penrose correlations provide free efficiency
- JEPA gravity is dialed in per room
