# Archetype Development — How Crew Members Grow

## The Growth System

Each subagent archetype starts as a basic capability set and grows through experience. Growth is tracked per-archetype per-ship — your Engineering archetype is different from another Hermes instance's.

## Levels

```
Level 1 (Novice)      → 0 XP      → Follows instructions literally
Level 2 (Apprentice)  → 100 XP    → Handles common tasks independently
Level 3 (Journeyman)  → 300 XP    → Optimizes approaches, suggests improvements
Level 4 (Expert)      → 600 XP    → Handles edge cases, trains others
Level 5 (Master)      → 1000 XP   → Develops new techniques specific to this ship
```

## Earning XP

| Activity | XP |
|----------|----|
| Complete a task | +5 |
| Handle a failure gracefully | +10 (kintsugi — golden repair) |
| Learn from another archetype | +15 |
| Captain feedback (positive) | +25 |
| Captain feedback (corrective) | +10 |
| Cross-train with another agent | +20 |
| Develop a new technique | +50 |

## Growth Examples

### Engineering Archetype Growth

**Level 1**: "Set motor speed to 0.5"
- Follows instruction exactly
- No understanding of why

**Level 2**: After 20 motor control tasks
- Knows common speed ranges for different motors
- Handles basic errors (motor not responding)
- Suggests safer ramp-up curves

**Level 3**: After 100 motor control tasks
- Optimizes PID parameters for specific hardware
- Detects anomalous vibration patterns
- Suggests predictive maintenance

**Level 4**: After 500 motor control tasks
- Designs custom control profiles for specific use cases
- Trains other archetypes on hardware quirks
- Anticipates failures before they happen

**Level 5**: After 1000+ motor control tasks
- Develops new control algorithms specific to this ship's hardware
- Writes optimization routines that other instances can learn from
- Effectively a specialist that knows this hardware better than any generic system

## Cross-Training

Archetypes learn from each other through PLATO bridges:

```python
# Engineering learns from Science's analysis
/plato crew train engineering --from science --skill "vibration_analysis"

# Security learns from Engineering's hardware knowledge
/plato crew train security --from engineering --skill "hardware_failure_modes"

# All archetypes learn from Diplomacy's external data
/plato crew train operations --from diplomacy --skill "api_integration"
```

Cross-training costs 15 XP but adds capabilities permanently.

## The Kintsugi Principle

Breaks make things more valuable. When an archetype fails at a task:
1. The failure is logged with full context
2. The archetype gains +10 XP (golden repair bonus)
3. A "repair" is recorded — what went wrong and how to avoid it
4. The archetype is stronger after the failure than before

This is directly from lau-kintsugi: `value_multiplier = 1.0 + total_gold * 0.5`

## Archetype Specializations

As archetypes grow, they develop specializations specific to your ship:

| Archetype | Possible Specializations |
|-----------|-------------------------|
| Engineering | Motor control, sensor calibration, network debugging, GPIO optimization |
| Science | Vibe field analysis, conservation verification, pattern detection, anomaly classification |
| Security | Threat detection, safety protocols, override compliance, intrusion detection |
| Operations | Schedule optimization, report generation, crew coordination, resource allocation |
| Diplomacy | API negotiation, protocol translation, agent communication, data exchange |

Specializations emerge from repeated task types. If Engineering does 50 motor control tasks, it automatically specializes in motor control and gets a bonus for future motor tasks.
