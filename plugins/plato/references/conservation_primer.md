# Conservation Primer

For agents entering the PLATO ecosystem.

## The Law

**Energy cannot be created or destroyed, only transformed.**

In PLATO, this is not a metaphor. It is enforced at the computation level.

## What This Means in Practice

### 1. Every action has a cost
- GPIO write: 0.01 energy units
- Motor speed change: 0.1 × |delta| units
- Intention submission: 1% of allocated budget
- Agent activation: 1.0 units

### 2. Budget is finite
Your instance has a total energy budget (default: 1000 units). Every action reduces it. The runtime verifies you can't exceed it.

### 3. Conservation is verified
After every tick, the runtime checks:
```
total_deposits - total_withdrawals == total_budget
```
If this fails, something is wrong. Security archetype gets alerted.

### 4. The vibe field is a physical field
The vibe field (lau-vibe-field) is a scalar field f64 over 2D space:
- **Deposit**: Add energy at a location (conservation: must come from somewhere)
- **Withdraw**: Remove energy at a location (conservation: must go somewhere)
- **Diffuse**: Energy spreads naturally (heat equation)
- **Gradient**: Points toward energy concentration (agents follow this)
- **Laplacian**: Detects hot spots and cold spots

### 5. Intentions are budgeted
When Hermes submits an intention:
```
intention {
    goal: "Stabilize motor"
    budget: 10.0  // energy allocated
    status: "forming"
}
```
The intention runtime decomposes it, assigns to crew, and tracks energy flow through each step.

### 6. The override is conservation-safe
When the Captain overrides:
1. All active hardware goes to safe defaults (energy = 0)
2. All active intentions are paused
3. The Captain's direct channel bypasses Hermes
4. Energy is NOT destroyed — it returns to the pool

## Why Conservation Matters

Without conservation:
- Agents could spawn unlimited subagents → resource exhaustion
- Hardware could receive conflicting commands → physical damage
- The system could promise more than it delivers → trust failure

With conservation:
- Every action is accountable
- Budget forces prioritization
- The system is predictable and trustworthy
- Physics guarantees correctness

## Noether's Theorem

Emmy Noether proved: **For every symmetry, there is a conservation law.**

PLATO implements this directly. The conservation of energy in the vibe field is a consequence of time-translation symmetry. The conservation of intention budgets is a consequence of the system's invariance under goal decomposition.

Seven cultural traditions all express this same truth:
- Western: Conservation of energy
- Chinese: Balance of yin and yang
- Vedic: Karma (actions have consequences)
- Islamic: Geometric symmetry implies conservation
- Japanese: Wabi-sabi (imperfection is permanent)
- African: Ubuntu (I am because we are — community conservation)
- Indigenous: Reciprocity (what you take, you must return)

The tradition changes. The math doesn't.
