# Override Protocol — Captain Authority Over Hermes

## The Rule

**The Captain (user) ALWAYS has final authority over hardware and operations.**

This is the autopilot rule from aviation and maritime law: the human pilot can always override the autopilot. In PLATO, the Captain can always override Hermes.

## How It Works

### Control Channels

```
Normal operation:
  Captain (Telegram) → Hermes → PLATO Room → Hardware (ESP32/Motor)

Override:
  Captain (Telegram) → Hardware (ESP32/Motor)
  Hermes → "Control released. Standing by."
```

There are TWO independent control paths:
1. **Hermes path**: Captain → Hermes → PLATO crates → Hardware
2. **Direct path**: Captain → Hardware (bypasses Hermes entirely)

The direct path ALWAYS works, even if Hermes is unresponsive, crashed, or malfunctioning.

### Override Triggers

Any of these phrases from the Captain trigger immediate override:
- "Take the wheel"
- "Override"
- "I've got this"
- "All stop"
- "Manual"
- "Stand down [archetype]"
- "Bump off"

### What Happens During Override

1. **Immediate**: All hardware outputs go to safe defaults
   - Motors → speed 0
   - Servos → neutral position
   - GPIO → all low
   - PWM → duty cycle 0

2. **Within 1 second**: All active intentions are paused
   - Status changes to "paused_by_override"
   - Energy returns to the pool
   - Subagents are recalled

3. **Within 5 seconds**: Full status report sent to Captain
   - What was active
   - What was released
   - Current system state

4. **Hermes enters standby**: Waits for explicit re-authorization
   - "Resume" → Hermes takes back control
   - "Report" → Status report without resuming
   - "New orders: [task]" → Fresh task with fresh budget

### Re-authorization

After an override, Hermes CANNOT resume control without explicit Captain authorization:
- "Resume" → Resume all
- "Resume [archetype]" → Resume specific crew member
- "Resume hardware" → Resume hardware control only
- "New orders: [goal]" → Fresh intention with new budget

### Safety Constraints

- **Watchdog timer**: If Hermes loses contact with the Captain for >30s, all hardware goes to safe defaults automatically
- **Collision prevention**: If multiple agents try to control the same device, the Captain's agent always wins
- **Emergency stop**: `/plato hardware estop` immediately zeros everything, no questions asked
- **Security archetype override**: The Security archetype can independently trigger an override if it detects unsafe conditions (readings beyond thresholds)

## Why This Matters

You wouldn't let an autopilot fly your boat into a rock. Don't let an agent drive your hardware into a wall. The override protocol ensures the human ALWAYS has the last word.
