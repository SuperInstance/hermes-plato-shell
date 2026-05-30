---
name: plato-subagent-archetypes
description: Manage specialized crew archetypes that grow with your ship.
version: 0.1.0
author: SuperInstance
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [plato, subagents, crew, archetypes, delegation]
    category: plato
---

# PLATO Subagent Archetypes Skill

Manage your crew of specialized subagent archetypes. Each archetype starts as a basic capability set and grows with experience specific to YOUR ship.

## When to Use

- Activating or deactivating crew members
- Assigning tasks to the right specialist
- Training an archetype on new skills
- Reviewing crew performance and growth
- The Captain asks about crew capabilities

## The Five Archetypes

### 1. Engineering ⚙️
**Specializes in**: Systems, hardware, motor controllers, ESP32 rooms, GPIO, infrastructure
**Default tools**: terminal, file operations, hardware bridge
**Grows with**: Each hardware task completed, each sensor calibrated, each motor tuned
**Personality**: Methodical, safety-conscious, loves optimization

```python
/plato crew activate engineering
/plato crew assign engineering "Calibrate motor 3 PID loop"
/plato crew status engineering  # Shows experience level, tasks completed, specializations gained
```

### 2. Science 🔬
**Specializes in**: Analysis, conservation verification, pattern detection, data interpretation
**Default tools**: terminal, code execution, search
**Grows with**: Each analysis completed, each anomaly detected, each conservation verification passed
**Personality**: Curious, rigorous, loves finding patterns

```python
/plato crew activate science
/plato crew assign science "Analyze vibe field gradient and identify energy hotspots"
/plato crew status science  # Shows analysis depth, pattern recognition level
```

### 3. Security 🛡️
**Specializes in**: Monitoring, anomaly detection, safety enforcement, override compliance
**Default tools**: terminal, monitoring, logging
**Grows with**: Each anomaly caught, each safety protocol executed, each threat assessed
**Personality**: Vigilant, decisive, never compromises on safety

```python
/plato crew activate security
/plato crew assign security "Monitor all hardware for anomalous readings, alert on threshold"
/plato crew status security  # Shows threat detection rate, false positive rate, response time
```

### 4. Operations 📋
**Specializes in**: Scheduling, logistics, communication, coordination, reporting
**Default tools**: terminal, cron, messaging
**Grows with**: Each schedule optimized, each report delivered, each coordination completed
**Personality**: Organized, proactive, keeps everything running

```python
/plato crew activate operations
/plato crew assign operations "Schedule daily sensor calibration for 0600, report to Captain"
/plato crew status operations  # Shows scheduling efficiency, coordination history
```

### 5. Diplomacy 🤝
**Specializes in**: External communication, API negotiation, coworker collaboration, PLATO bridge management
**Default tools**: terminal, messaging, web
**Grows with**: Each successful negotiation, each external query handled, each bridge maintained
**Personality**: Polite, adaptable, represents the ship well

```python
/plato crew activate diplomacy
/plato crew assign diplomacy "Query openclaw-main for the latest conservation budget allocation"
/plato crew status diplomacy  # Shows external connections, negotiation success rate
```

## Archetype Growth

Archetypes grow through experience. The growth is tracked per-archetype per-ship:

```
Level 1 (Novice):      Basic capabilities, follows instructions literally
Level 2 (Apprentice):  Handles common tasks independently
Level 3 (Journeyman):  Optimizes approaches, suggests improvements
Level 4 (Expert):      Handles edge cases, trains other archetypes
Level 5 (Master):      Develops new techniques specific to this ship
```

Growth is driven by:
- **Task completion**: Each successful task adds experience
- **Error recovery**: Learning from failures (kintsugi — golden repairs)
- **Cross-training**: Archetypes learning from each other through PLATO bridges
- **Captain feedback**: Explicit feedback accelerates growth

## Crew Management

```python
# List all crew and status
/plato crew roster

# Activate an archetype (brings it online)
/plato crew activate <name>

# Stand down an archetype (takes it offline)
/plato crew stand_down <name>

# Assign a task to specific archetype
/plato crew assign <name> "task description"

# Auto-assign: let Hermes pick the right archetype
/plato crew auto "task description"

# Train an archetype with new knowledge
/plato crew train <name> --from "knowledge source"

# Get detailed status
/plato crew status <name>

# Review growth history
/plato crew history <name>
```

## How Archetypes Map to Hermes Subagents

Each PLATO archetype is implemented as a Hermes subagent with:
- **Specific toolset**: Engineering gets hardware tools, Science gets analysis tools
- **Custom system prompt**: Tailored to the archetype's personality and role
- **Experience file**: `~/.hermes/plato/crew/<archetype>.yaml` tracks growth
- **Delegated tasks**: Hermes uses `delegate_task` with role-specific configurations

The archetype configuration is stored in `~/.hermes/plato/crew/<archetype>.yaml`:

```yaml
name: engineering
level: 1
experience_points: 0
tasks_completed: 0
tasks_failed: 0
specializations: []
personality:
  style: methodical
  risk_tolerance: low
  communication: concise
growth_log:
  - task: "Initial calibration"
    result: success
    xp_gained: 10
    timestamp: "2026-05-30T13:00:00Z"
```

## Pitfalls

- **Don't activate all archetypes at once.** Each consumes resources. Activate what you need.
- **Archetypes are ship-specific.** Your Engineering archetype is different from another Hermes instance's Engineering. The growth is local.
- **Security archetype has special authority.** It can trigger overrides independently when safety is at risk.
- **Respect the hierarchy.** Archetypes answer to Hermes. Hermes answers to the Captain.
- **Stand down archetypes you're not using.** Conserves energy and compute.
