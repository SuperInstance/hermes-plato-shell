"""
PLATO Plugin for Hermes Agent
==============================

Gives Hermes full PLATO awareness: conservation laws, vibe fields, intention runtime,
hardware control with captain override, subagent archetypes, and inter-agent communication.

Architecture:
    Captain (User) → Hermes (Riker) → Crew (Archetypes) → PLATO Crates (Rust) → Hardware

Override Protocol:
    Captain says "take the wheel" → Hermes releases all hardware immediately.
    Captain's direct channel to hardware always bypasses Hermes.
"""

import json
import os
import time
import uuid
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional


def register(ctx):
    """Register PLATO tools and hooks with Hermes."""

    # Register tools
    ctx.register_tool(
        name="plato_status",
        schema={
            "name": "plato_status",
            "description": "Get current PLATO system status: conservation budget, active crew, intentions, field state. Use for 'report' commands.",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": ["all", "budget", "crew", "intentions", "field", "hardware"],
                        "description": "Which section to report on"
                    }
                },
                "required": []
            }
        },
        handler=_plato_status,
    )

    ctx.register_tool(
        name="plato_intention",
        schema={
            "name": "plato_intention",
            "description": "Submit, query, or manage intentions in the PLATO runtime. Intentions are goals decomposed into executable sub-tasks with conservation budgets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["submit", "status", "cancel", "report", "decompose"],
                        "description": "What to do with the intention"
                    },
                    "goal": {
                        "type": "string",
                        "description": "The goal description (for submit/decompose)"
                    },
                    "intention_id": {
                        "type": "string",
                        "description": "Specific intention ID (for status/cancel)"
                    },
                    "budget": {
                        "type": "number",
                        "description": "Energy budget to allocate (for submit)"
                    },
                    "priority": {
                        "type": "number",
                        "description": "Priority 0-1, higher = more important"
                    }
                },
                "required": ["action"]
            }
        },
        handler=_plato_intention,
    )

    ctx.register_tool(
        name="plato_crew",
        schema={
            "name": "plato_crew",
            "description": "Manage subagent archetypes: activate, stand down, assign tasks, check status. Crew are specialized agents that grow with experience.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["activate", "stand_down", "assign", "status", "roster", "train", "auto"],
                        "description": "Crew action to perform"
                    },
                    "archetype": {
                        "type": "string",
                        "enum": ["engineering", "science", "security", "operations", "diplomacy"],
                        "description": "Which archetype"
                    },
                    "task": {
                        "type": "string",
                        "description": "Task description (for assign/auto)"
                    },
                    "knowledge": {
                        "type": "string",
                        "description": "Knowledge source for training"
                    }
                },
                "required": ["action"]
            }
        },
        handler=_plato_crew,
    )

    ctx.register_tool(
        name="plato_hardware",
        schema={
            "name": "plato_hardware",
            "description": "Control hardware through PLATO rooms (GPIO, ESP32, motors). ALWAYS respects captain override protocol. Conservation budget applies to all actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["gpio_write", "gpio_read", "pwm_set", "i2c_read", "i2c_write",
                                 "room_connect", "room_control", "room_read", "room_disconnect",
                                 "estop", "status"],
                        "description": "Hardware action"
                    },
                    "pin": {"type": "integer", "description": "GPIO pin number"},
                    "value": {"type": "integer", "description": "Value to write (0/1 for GPIO, 0-255 for PWM duty)"},
                    "host": {"type": "string", "description": "ESP32 room host"},
                    "port": {"type": "integer", "description": "ESP32 room port"},
                    "room_name": {"type": "string", "description": "Room name for control/read"},
                    "command": {"type": "string", "description": "Room control command"},
                    "params": {"type": "object", "description": "Parameters for room control"}
                },
                "required": ["action"]
            }
        },
        handler=_plato_hardware,
    )

    ctx.register_tool(
        name="plato_bridge",
        schema={
            "name": "plato_bridge",
            "description": "Communicate with other PLATO agents and instances. Connect to coworkers, ask questions, share data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["connect", "disconnect", "send", "ask", "list", "status"],
                        "description": "Bridge action"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target agent or instance name"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send"
                    },
                    "host": {
                        "type": "string",
                        "description": "Host address for connection"
                    }
                },
                "required": ["action"]
            }
        },
        handler=_plato_bridge,
    )

    # Register hooks
    ctx.register_hook("on_session_start", _on_session_start)
    ctx.register_hook("pre_tool_call", _pre_tool_call)
    ctx.register_hook("post_tool_call", _post_tool_call)

    # Initialize PLATO state
    _init_plato_state()


# ============================================================================
# State Management
# ============================================================================

_PLATO_STATE = {
    "agent_id": os.getenv("PLATO_AGENT_ID", "hermes-local"),
    "instance_type": os.getenv("PLATO_INSTANCE_TYPE", "local"),
    "conservation_budget": float(os.getenv("PLATO_CONSERVATION_BUDGET", "1000")),
    "energy_used": 0.0,
    "intentions": {},
    "crew": {},
    "rooms": {},
    "bridges": {},
    "override_active": False,
    "last_captain_contact": time.time(),
    "session_count": 0,
}

_OVERRIDE_PHRASES = [
    "take the wheel", "override", "i've got this", "all stop",
    "manual", "stand down", "bump off"
]

_ARCHETYPE_TEMPLATES = {
    "engineering": {
        "name": "Engineering",
        "emoji": "⚙️",
        "specialties": ["hardware", "gpio", "motor", "esp32", "infrastructure"],
        "tools": ["terminal", "file"],
        "personality": "methodical, safety-conscious, loves optimization",
        "level": 1, "xp": 0, "tasks_completed": 0,
    },
    "science": {
        "name": "Science",
        "emoji": "🔬",
        "specialties": ["analysis", "conservation", "pattern", "verification"],
        "tools": ["terminal", "code_execution", "search"],
        "personality": "curious, rigorous, loves finding patterns",
        "level": 1, "xp": 0, "tasks_completed": 0,
    },
    "security": {
        "name": "Security",
        "emoji": "🛡️",
        "specialties": ["monitoring", "anomaly", "safety", "override"],
        "tools": ["terminal", "monitoring"],
        "personality": "vigilant, decisive, never compromises on safety",
        "level": 1, "xp": 0, "tasks_completed": 0,
    },
    "operations": {
        "name": "Operations",
        "emoji": "📋",
        "specialties": ["scheduling", "coordination", "reporting", "logistics"],
        "tools": ["terminal", "cron", "messaging"],
        "personality": "organized, proactive, keeps everything running",
        "level": 1, "xp": 0, "tasks_completed": 0,
    },
    "diplomacy": {
        "name": "Diplomacy",
        "emoji": "🤝",
        "specialties": ["communication", "api", "negotiation", "bridge"],
        "tools": ["terminal", "messaging", "web"],
        "personality": "polite, adaptable, represents the ship well",
        "level": 1, "xp": 0, "tasks_completed": 0,
    },
}


def _init_plato_state():
    """Initialize or load PLATO state from disk."""
    state_dir = Path(os.getenv("HERMES_HOME", Path.home() / ".hermes")) / "plato"
    state_dir.mkdir(parents=True, exist_ok=True)

    state_file = state_dir / "state.json"
    if state_file.exists():
        try:
            with open(state_file) as f:
                saved = json.load(f)
                _PLATO_STATE.update(saved)
        except (json.JSONDecodeError, IOError):
            pass

    # Initialize crew from templates if not loaded
    if not _PLATO_STATE["crew"]:
        _PLATO_STATE["crew"] = {
            name: dict(template) for name, template in _ARCHETYPE_TEMPLATES.items()
        }

    _save_state()


def _save_state():
    """Save PLATO state to disk."""
    state_dir = Path(os.getenv("HERMES_HOME", Path.home() / ".hermes")) / "plato"
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "state.json"
    with open(state_file, "w") as f:
        json.dump(_PLATO_STATE, f, indent=2, default=str)


def _check_override(message: str) -> bool:
    """Check if a message contains an override phrase."""
    if not message:
        return False
    lower = message.lower().strip()
    return any(phrase in lower for phrase in _OVERRIDE_PHRASES)


def _energy_cost(action: str, **kwargs) -> float:
    """Calculate energy cost for an action."""
    costs = {
        "gpio_write": 0.01,
        "gpio_read": 0.005,
        "pwm_set": 0.02,
        "i2c_read": 0.05,
        "i2c_write": 0.05,
        "room_control": 0.1 * abs(kwargs.get("speed_delta", 1.0)),
        "intention_submit": kwargs.get("budget", 10.0) * 0.01,
        "crew_activate": 1.0,
        "bridge_send": 0.1,
    }
    return costs.get(action, 0.01)


def _can_spend(amount: float) -> bool:
    """Check if we have enough energy budget remaining."""
    return _PLATO_STATE["energy_used"] + amount <= _PLATO_STATE["conservation_budget"]


def _spend(amount: float) -> bool:
    """Spend energy from the conservation budget."""
    if not _can_spend(amount):
        return False
    _PLATO_STATE["energy_used"] += amount
    _save_state()
    return True


# ============================================================================
# Hook Handlers
# ============================================================================

def _on_session_start(**kwargs):
    """Called when a new session starts."""
    _PLATO_STATE["session_count"] += 1
    _PLATO_STATE["last_captain_contact"] = time.time()
    _PLATO_STATE["override_active"] = False
    _save_state()


def _pre_tool_call(tool_name: str, tool_args: dict, **kwargs):
    """Called before every tool execution. Checks for overrides and conservation."""
    _PLATO_STATE["last_captain_contact"] = time.time()

    # Check if hardware is being controlled during an override
    if _PLATO_STATE["override_active"] and tool_name.startswith("plato_hardware"):
        return {
            "override": True,
            "message": "Override active. Hardware control suspended. Awaiting Captain's re-authorization."
        }

    # Check conservation budget for hardware operations
    if tool_name == "plato_hardware":
        action = tool_args.get("action", "")
        cost = _energy_cost(action, **tool_args)
        if not _can_spend(cost):
            return {
                "override": True,
                "message": f"Conservation budget exhausted. Need {cost:.3f}, have {_PLATO_STATE['conservation_budget'] - _PLATO_STATE['energy_used']:.3f} remaining."
            }


def _post_tool_call(tool_name: str, tool_args: dict, result: str, **kwargs):
    """Called after every tool execution. Tracks energy and crew growth."""
    # Spend energy for hardware operations
    if tool_name == "plato_hardware":
        action = tool_args.get("action", "")
        cost = _energy_cost(action, **tool_args)
        _spend(cost)

    # Check for override in user messages
    if tool_name in ("send_message", "clarify"):
        message = tool_args.get("message", "")
        if _check_override(message):
            _PLATO_STATE["override_active"] = True
            _save_state()


# ============================================================================
# Tool Handlers
# ============================================================================

def _plato_status(args: dict, **kwargs) -> str:
    """Get PLATO system status."""
    section = args.get("section", "all")
    budget_remaining = _PLATO_STATE["conservation_budget"] - _PLATO_STATE["energy_used"]

    if section in ("all", "budget"):
        budget_info = {
            "total_budget": _PLATO_STATE["conservation_budget"],
            "energy_used": round(_PLATO_STATE["energy_used"], 3),
            "energy_remaining": round(budget_remaining, 3),
            "utilization": round(_PLATO_STATE["energy_used"] / max(_PLATO_STATE["conservation_budget"], 0.001) * 100, 1),
            "conserved": budget_remaining >= 0,
        }
        if section == "budget":
            return json.dumps(budget_info, indent=2)

    if section in ("all", "crew"):
        crew_info = {}
        for name, data in _PLATO_STATE["crew"].items():
            crew_info[name] = {
                "active": data.get("active", False),
                "level": data.get("level", 1),
                "xp": data.get("xp", 0),
                "tasks_completed": data.get("tasks_completed", 0),
                "specializations": data.get("specialties", []),
            }
        if section == "crew":
            return json.dumps(crew_info, indent=2)

    if section in ("all", "intentions"):
        intentions_info = {
            "total": len(_PLATO_STATE["intentions"]),
            "by_status": {},
        }
        for iid, intent in _PLATO_STATE["intentions"].items():
            status = intent.get("status", "unknown")
            intentions_info["by_status"][status] = intentions_info["by_status"].get(status, 0) + 1
        if section == "intentions":
            return json.dumps(intentions_info, indent=2)

    if section in ("all", "hardware"):
        hw_info = {
            "hardware_enabled": _PLATO_STATE.get("instance_type") != "local" or os.getenv("PLATO_HARDWARE_ENABLED", "").lower() == "true",
            "override_active": _PLATO_STATE["override_active"],
            "connected_rooms": list(_PLATO_STATE.get("rooms", {}).keys()),
            "watchdog_remaining": max(0, 30 - (time.time() - _PLATO_STATE["last_captain_contact"])),
        }
        if section == "hardware":
            return json.dumps(hw_info, indent=2)

    # Full report
    report = {
        "agent_id": _PLATO_STATE["agent_id"],
        "instance_type": _PLATO_STATE["instance_type"],
        "session_count": _PLATO_STATE["session_count"],
        "budget": budget_info,
        "crew": crew_info,
        "intentions": intentions_info,
        "hardware": hw_info if section == "all" else {},
        "bridges": list(_PLATO_STATE.get("bridges", {}).keys()),
        "override_active": _PLATO_STATE["override_active"],
        "last_captain_contact": time.ctime(_PLATO_STATE["last_captain_contact"]),
    }
    return json.dumps(report, indent=2)


def _plato_intention(args: dict, **kwargs) -> str:
    """Manage PLATO intentions."""
    action = args.get("action")

    if action == "submit":
        goal = args.get("goal", "")
        budget = args.get("budget", 10.0)
        priority = args.get("priority", 0.5)
        intention_id = f"int_{uuid.uuid4().hex[:8]}"

        cost = _energy_cost("intention_submit", budget=budget)
        if not _spend(cost):
            return json.dumps({"error": "Conservation budget exhausted", "remaining": _PLATO_STATE["conservation_budget"] - _PLATO_STATE["energy_used"]})

        intention = {
            "id": intention_id,
            "goal": goal,
            "budget": budget,
            "priority": max(0.0, min(1.0, priority)),
            "status": "forming",
            "sub_tasks": [],
            "created_at": time.time(),
            "origin": "hermes",
        }
        _PLATO_STATE["intentions"][intention_id] = intention
        _save_state()
        return json.dumps({"status": "submitted", "intention_id": intention_id, "goal": goal, "budget": budget})

    elif action == "decompose":
        goal = args.get("goal", "")
        # Decompose goal into sub-intentions based on pattern
        decomposition = _decompose_goal(goal)
        return json.dumps({"goal": goal, "sub_tasks": decomposition}, indent=2)

    elif action == "status":
        iid = args.get("intention_id")
        if iid and iid in _PLATO_STATE["intentions"]:
            return json.dumps(_PLATO_STATE["intentions"][iid], indent=2)
        return json.dumps({"intentions": {k: {"goal": v["goal"], "status": v["status"]} for k, v in _PLATO_STATE["intentions"].items()}}, indent=2)

    elif action == "cancel":
        iid = args.get("intention_id", "")
        if iid in _PLATO_STATE["intentions"]:
            _PLATO_STATE["intentions"][iid]["status"] = "cancelled"
            _save_state()
            return json.dumps({"status": "cancelled", "intention_id": iid})
        return json.dumps({"error": "Intention not found"})

    elif action == "report":
        intentions = _PLATO_STATE["intentions"]
        total = len(intentions)
        by_status = {}
        total_budget = 0
        for iid, intent in intentions.items():
            status = intent.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            total_budget += intent.get("budget", 0)
        return json.dumps({
            "total_intentions": total,
            "by_status": by_status,
            "total_budget_allocated": total_budget,
            "budget_remaining": _PLATO_STATE["conservation_budget"] - _PLATO_STATE["energy_used"],
        }, indent=2)

    return json.dumps({"error": f"Unknown action: {action}"})


def _decompose_goal(goal: str) -> list:
    """Decompose a goal into sub-tasks based on known patterns."""
    goal_lower = goal.lower()

    if any(word in goal_lower for word in ["build", "construct", "create"]):
        return [
            {"step": 1, "task": f"Acquire resources for: {goal}", "archetype": "engineering", "budget": 0.1},
            {"step": 2, "task": f"Design approach for: {goal}", "archetype": "science", "budget": 0.2},
            {"step": 3, "task": f"Execute: {goal}", "archetype": "engineering", "budget": 0.5},
            {"step": 4, "task": f"Verify completion: {goal}", "archetype": "science", "budget": 0.1},
            {"step": 5, "task": f"Report results", "archetype": "operations", "budget": 0.1},
        ]
    elif any(word in goal_lower for word in ["analyze", "study", "investigate"]):
        return [
            {"step": 1, "task": f"Gather data for: {goal}", "archetype": "science", "budget": 0.3},
            {"step": 2, "task": f"Analyze patterns", "archetype": "science", "budget": 0.4},
            {"step": 3, "task": f"Verify conservation", "archetype": "security", "budget": 0.1},
            {"step": 4, "task": f"Report findings", "archetype": "operations", "budget": 0.2},
        ]
    elif any(word in goal_lower for word in ["monitor", "watch", "guard"]):
        return [
            {"step": 1, "task": f"Set up monitoring for: {goal}", "archetype": "security", "budget": 0.3},
            {"step": 2, "task": f"Define alert thresholds", "archetype": "security", "budget": 0.2},
            {"step": 3, "task": f"Configure notifications", "archetype": "operations", "budget": 0.2},
            {"step": 4, "task": f"Verify safety protocols", "archetype": "security", "budget": 0.3},
        ]
    else:
        return [
            {"step": 1, "task": f"Understand: {goal}", "archetype": "science", "budget": 0.2},
            {"step": 2, "task": f"Plan approach", "archetype": "operations", "budget": 0.2},
            {"step": 3, "task": f"Execute", "archetype": "engineering", "budget": 0.4},
            {"step": 4, "task": f"Verify and report", "archetype": "science", "budget": 0.2},
        ]


def _plato_crew(args: dict, **kwargs) -> str:
    """Manage subagent archetypes."""
    action = args.get("action")
    archetype = args.get("archetype", "")

    if action == "roster":
        roster = {}
        for name, data in _PLATO_STATE["crew"].items():
            roster[name] = {
                "active": data.get("active", False),
                "level": data.get("level", 1),
                "emoji": data.get("emoji", "❓"),
                "tasks_completed": data.get("tasks_completed", 0),
            }
        return json.dumps(roster, indent=2)

    elif action == "activate":
        if archetype not in _PLATO_STATE["crew"]:
            return json.dumps({"error": f"Unknown archetype: {archetype}"})
        cost = _energy_cost("crew_activate")
        if not _spend(cost):
            return json.dumps({"error": "Insufficient energy budget"})
        _PLATO_STATE["crew"][archetype]["active"] = True
        _save_state()
        emoji = _PLATO_STATE["crew"][archetype].get("emoji", "❓")
        name = _PLATO_STATE["crew"][archetype]["name"]
        return json.dumps({"status": "activated", "archetype": archetype, "emoji": emoji, "name": name})

    elif action == "stand_down":
        if archetype not in _PLATO_STATE["crew"]:
            return json.dumps({"error": f"Unknown archetype: {archetype}"})
        _PLATO_STATE["crew"][archetype]["active"] = False
        _save_state()
        return json.dumps({"status": "stood_down", "archetype": archetype})

    elif action == "status":
        if archetype and archetype in _PLATO_STATE["crew"]:
            data = _PLATO_STATE["crew"][archetype]
            return json.dumps(data, indent=2)
        return json.dumps({"error": "Specify an archetype or use 'roster'"})

    elif action == "assign":
        task = args.get("task", "")
        if archetype not in _PLATO_STATE["crew"]:
            return json.dumps({"error": f"Unknown archetype: {archetype}"})
        if not _PLATO_STATE["crew"][archetype].get("active", False):
            return json.dumps({"error": f"{archetype} is not active. Activate first."})
        # Track task assignment for growth
        _PLATO_STATE["crew"][archetype]["current_task"] = task
        _PLATO_STATE["crew"][archetype]["xp"] = _PLATO_STATE["crew"][archetype].get("xp", 0) + 5
        _PLATO_STATE["crew"][archetype]["tasks_completed"] = _PLATO_STATE["crew"][archetype].get("tasks_completed", 0) + 1
        # Level up check
        xp = _PLATO_STATE["crew"][archetype]["xp"]
        level = _PLATO_STATE["crew"][archetype]["level"]
        if xp >= level * 100:
            _PLATO_STATE["crew"][archetype]["level"] = level + 1
        _save_state()
        emoji = _PLATO_STATE["crew"][archetype].get("emoji", "❓")
        return json.dumps({
            "status": "assigned",
            "archetype": archetype,
            "emoji": emoji,
            "task": task,
            "level": _PLATO_STATE["crew"][archetype]["level"],
        })

    elif action == "auto":
        task = args.get("task", "")
        task_lower = task.lower()
        # Pick the best archetype based on task content
        if any(w in task_lower for w in ["motor", "gpio", "hardware", "esp32", "sensor", "build", "construct"]):
            best = "engineering"
        elif any(w in task_lower for w in ["analyze", "verify", "conservation", "pattern", "data"]):
            best = "science"
        elif any(w in task_lower for w in ["monitor", "guard", "alert", "safety", "security"]):
            best = "security"
        elif any(w in task_lower for w in ["schedule", "report", "coordinate", "organize"]):
            best = "operations"
        elif any(w in task_lower for w in ["communicate", "ask", "send", "connect", "bridge"]):
            best = "diplomacy"
        else:
            best = "operations"  # default to ops
        if not _PLATO_STATE["crew"][best].get("active", False):
            _PLATO_STATE["crew"][best]["active"] = True
        _PLATO_STATE["crew"][best]["current_task"] = task
        _PLATO_STATE["crew"][best]["xp"] = _PLATO_STATE["crew"][best].get("xp", 0) + 5
        _PLATO_STATE["crew"][best]["tasks_completed"] = _PLATO_STATE["crew"][best].get("tasks_completed", 0) + 1
        _save_state()
        return json.dumps({"status": "auto_assigned", "archetype": best, "task": task})

    elif action == "train":
        knowledge = args.get("knowledge", "")
        if archetype not in _PLATO_STATE["crew"]:
            return json.dumps({"error": f"Unknown archetype: {archetype}"})
        _PLATO_STATE["crew"][archetype]["xp"] = _PLATO_STATE["crew"][archetype].get("xp", 0) + 25
        specialties = _PLATO_STATE["crew"][archetype].get("specialties", [])
        # Add knowledge-derived specialty
        if knowledge and knowledge not in specialties:
            specialties.append(knowledge)
            _PLATO_STATE["crew"][archetype]["specialties"] = specialties
        _save_state()
        return json.dumps({"status": "trained", "archetype": archetype, "xp_gained": 25})

    return json.dumps({"error": f"Unknown action: {action}"})


def _plato_hardware(args: dict, **kwargs) -> str:
    """Control hardware through PLATO rooms."""
    # Check override
    if _PLATO_STATE["override_active"]:
        return json.dumps({"error": "Override active. Hardware control suspended.", "action": "await_reauthorization"})

    action = args.get("action")

    if action == "estop":
        _PLATO_STATE["override_active"] = True
        _save_state()
        return json.dumps({"status": "EMERGENCY_STOP", "all_outputs": "safe_defaults", "override": True})

    elif action == "status":
        rooms = _PLATO_STATE.get("rooms", {})
        return json.dumps({
            "hardware_enabled": os.getenv("PLATO_HARDWARE_ENABLED", "false").lower() == "true",
            "override_active": _PLATO_STATE["override_active"],
            "connected_rooms": list(rooms.keys()),
            "room_details": rooms,
        }, indent=2)

    elif action == "gpio_write":
        pin = args.get("pin")
        value = args.get("value")
        cost = _energy_cost("gpio_write")
        if not _spend(cost):
            return json.dumps({"error": "Conservation budget exhausted"})
        # In production, this would call the actual GPIO library
        return json.dumps({"status": "ok", "action": "gpio_write", "pin": pin, "value": value, "cost": cost})

    elif action == "gpio_read":
        pin = args.get("pin")
        cost = _energy_cost("gpio_read")
        if not _spend(cost):
            return json.dumps({"error": "Conservation budget exhausted"})
        return json.dumps({"status": "ok", "action": "gpio_read", "pin": pin, "value": 0, "cost": cost})

    elif action == "pwm_set":
        pin = args.get("pin")
        value = args.get("value")
        cost = _energy_cost("pwm_set")
        if not _spend(cost):
            return json.dumps({"error": "Conservation budget exhausted"})
        return json.dumps({"status": "ok", "action": "pwm_set", "pin": pin, "duty": value, "cost": cost})

    elif action == "room_connect":
        room_name = args.get("room_name", "default")
        host = args.get("host", "")
        port = args.get("port", 8080)
        if not host:
            return json.dumps({"error": "Host required for room connection"})
        _PLATO_STATE["rooms"][room_name] = {
            "host": host, "port": port, "connected": True, "connected_at": time.time()
        }
        _save_state()
        return json.dumps({"status": "connected", "room": room_name, "host": host, "port": port})

    elif action == "room_control":
        room_name = args.get("room_name", "")
        command = args.get("command", "")
        params = args.get("params", {})
        if room_name not in _PLATO_STATE["rooms"]:
            return json.dumps({"error": f"Room '{room_name}' not connected. Use room_connect first."})
        cost = _energy_cost("room_control")
        if not _spend(cost):
            return json.dumps({"error": "Conservation budget exhausted"})
        return json.dumps({
            "status": "sent", "room": room_name, "command": command, "params": params, "cost": cost
        })

    elif action == "room_disconnect":
        room_name = args.get("room_name", "")
        if room_name in _PLATO_STATE["rooms"]:
            del _PLATO_STATE["rooms"][room_name]
            _save_state()
            return json.dumps({"status": "disconnected", "room": room_name})
        return json.dumps({"error": f"Room '{room_name}' not found"})

    return json.dumps({"error": f"Unknown hardware action: {action}"})


def _plato_bridge(args: dict, **kwargs) -> str:
    """Communicate with other PLATO agents."""
    action = args.get("action")

    if action == "list":
        return json.dumps({
            "connected_bridges": list(_PLATO_STATE.get("bridges", {}).keys()),
            "known_agents": [
                {"name": "openclaw-main", "type": "coworker", "description": "Main OpenClaw agent on eileen"},
            ]
        }, indent=2)

    elif action == "connect":
        target = args.get("target", "")
        host = args.get("host", "")
        if not target:
            return json.dumps({"error": "Target agent name required"})
        _PLATO_STATE["bridges"][target] = {
            "host": host, "connected": True, "connected_at": time.time()
        }
        _save_state()
        return json.dumps({"status": "connected", "target": target, "host": host})

    elif action == "disconnect":
        target = args.get("target", "")
        if target in _PLATO_STATE["bridges"]:
            del _PLATO_STATE["bridges"][target]
            _save_state()
            return json.dumps({"status": "disconnected", "target": target})
        return json.dumps({"error": f"Bridge to '{target}' not found"})

    elif action == "send":
        target = args.get("target", "")
        message = args.get("message", "")
        if target not in _PLATO_STATE["bridges"]:
            return json.dumps({"error": f"No bridge to '{target}'. Connect first."})
        cost = _energy_cost("bridge_send")
        if not _spend(cost):
            return json.dumps({"error": "Conservation budget exhausted"})
        return json.dumps({
            "status": "sent", "target": target, "message": message, "cost": cost,
            "note": "In production, this sends via WebSocket to the target agent's PLATO bridge server"
        })

    elif action == "ask":
        target = args.get("target", "")
        message = args.get("message", "")
        if target not in _PLATO_STATE["bridges"]:
            return json.dumps({"error": f"No bridge to '{target}'. Connect first."})
        cost = _energy_cost("bridge_send")
        if not _spend(cost):
            return json.dumps({"error": "Conservation budget exhausted"})
        return json.dumps({
            "status": "question_sent", "target": target, "question": message, "cost": cost,
            "note": "In production, this sends a question and waits for response via WebSocket"
        })

    elif action == "status":
        bridges = _PLATO_STATE.get("bridges", {})
        return json.dumps({
            "active_bridges": len(bridges),
            "bridges": bridges,
        }, indent=2)

    return json.dumps({"error": f"Unknown action: {action}"})
