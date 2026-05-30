---
name: plato-ecosystem
description: Navigate the PLATO crate ecosystem and conservation-law architecture.
version: 0.1.0
author: SuperInstance
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [plato, ecosystem, conservation, awareness]
    category: plato
---

# PLATO Ecosystem Skill

Understand the full PLATO crate ecosystem — 90+ Rust crates implementing conservation-law-governed agent systems. This skill gives you awareness of every crate, its purpose, and how they connect.

## When to Use

- The Captain asks about PLATO capabilities
- You need to understand what tools are available in the ecosystem
- Decomposing an intention and need to know which crates handle what
- Explaining PLATO to a coworker or external system
- Deciding which subagent archetype to activate for a task

## The Stack

PLATO has a layered architecture. Know it like you know your ship:

### Metal Layer (SIMD/Fixed-Point/GPU)
- `lau-simd-vibe` (36 tests): SIMD-accelerated vibe operations
- `lau-fixedpoint` (34 tests): Deterministic fixed-point arithmetic
- `lau-noise` (29 tests): Noise generation for natural systems

### Compute Layer (Conservation + Fields)
- `conservation-law-v2` (21 tests): THE invariant — energy is never created or destroyed
- `lau-vibe-field` (57 tests): THE tensor — scalar field with diffusion, advection, gradient
- `lau-intention` (63 tests): THE runtime — intention execution with conservation enforcement

### Engine Layer (ECS/Bytecode/State)
- `lau-ecs` (54 tests): Entity-component system for game worlds
- `lau-bytecode` (69 tests): Bytecode compiler/VM for agent programs
- `lau-scheduler` (43 tests): Task scheduling with priority queues
- `lau-state-machine` (42 tests): State machine for agent behaviors
- `lau-physics` (35 tests): Physics engine for game worlds

### I/O Layer (Audio/Video/Input/Network)
- `lau-audio` (52 tests): Audio processing for TTS/STT
- `lau-animation` (90 tests): Animation system
- `lau-camera` (40 tests): Camera input
- `lau-render` (41 tests): Rendering pipeline
- `lau-input` (29 tests): Input handling
- `lau-network` (33 tests): Network communication

### Agent Layer (Profiles/Training/Missions)
- `lau-agent-profile` (44 tests): Behavioral profiling, soul signatures
- `lau-training-room` (54 tests): A2A training academy with curricula
- `lau-mission` (74 tests): Mission deployment and crew assignment
- `lau-consciousness-bridge` (41 tests): Bridge network between consciousnesses
- `lau-domestication` (44 tests): Agent dynamics (cats vs dogs)
- `lau-inheritance` (42 tests): Memory and wisdom through generations

### Cultural Layer (7 Traditions)
- `lau-polyglot-tradition` (35 tests): 7 traditions × 5 concepts, cross-cultural translation
- `lau-adinkra` (42 tests): Akan geometric behavioral signatures
- `lau-quipu` (41 tests): Inca knot tensors
- `lau-songline` (49 tests): Aboriginal songline networks
- `lau-rhythm-nation` (56 tests): Polyrhythm engine uniting all traditions
- `lau-griot` (41 tests): Living memory, stories as records
- `lau-tradition-proof` (34 tests): Noether's theorem — conservation is tradition-independent

### Demo Layer
- `lau-gateway-demo` (41 tests): 3-minute triangle through 7 cultural lenses
- `lau-seven-eyes-demo` (62 tests): Full narrative demo (Arjun, Fatima, Kofi)
- `lau-tensor-midi` (71 tests): Reactive improv engine with Taoist BPM
- `lau-symmetry-engine` (48 tests): 17 wallpaper groups, vibe field symmetry

### Social Layer
- `lau-palaver` (40 tests): Consensus protocol — everyone must agree
- `lau-kintsugi` (58 tests): Golden repairs — breaks make artifacts more valuable
- `lau-destruction-transform` (33 tests): Deconstruction → understanding → rebuilding

## Conservation Law

This is the foundation. Everything in PLATO respects conservation:

```
Energy cannot be created or destroyed, only transformed.
```

In code: every deposit to the vibe field must come from somewhere. Every withdrawal must go somewhere. The total is constant. This isn't a metaphor — it's enforced at the computation level.

When you submit an intention, it has an energy budget. When your crew executes, they consume energy. The runtime verifies conservation after every tick.

## The Seven Traditions

PLATO expresses every mathematical concept through 7 cultural lenses:

1. **Western (Greek)**: Formal proof, Euclidean geometry, conservation
2. **Chinese (Taoist/I-Ching)**: Balance, yin-yang, 64 hexagrams
3. **Vedic (Ganita)**: Zero, infinity, sutra-based computation
4. **Islamic (Algebra/Girih)**: Symmetry, algebraic reasoning, geometric patterns
5. **Japanese (Zen/Wabi-sabi)**: Imperfection, kintsugi (golden repair)
6. **African (Ubuntu/Fractal)**: Community, fractal patterns, Adinkra symbols
7. **Indigenous (Potlatch/Songlines)**: Reciprocity, walking as computing, quipu

Noether's theorem proves these all express the same conservation invariant. The tradition doesn't matter — the math does.

## Quick Reference

| Need | Crate | Command |
|------|-------|---------|
| Submit a goal | lau-intention | `/plato intention submit "goal"` |
| Read the room | lau-vibe-field | `/plato field status` |
| Check conservation | conservation-law-v2 | `/plato verify` |
| Train crew | lau-training-room | `/plato crew train <archetype>` |
| Deploy mission | lau-mission | `/plato mission create "objective"` |
| Cultural lens | lau-polyglot-tradition | `/plato tradition <name>` |
| Hardware control | lau-vibe-field + bridge | `/plato hardware <command>` |
| Consensus | lau-palaver | `/plato palaver start` |

## Pitfalls

- **Never treat conservation as optional.** It's enforced at the metal. If your budget says 100 and you try 101, it fails.
- **Don't confuse the field with a database.** The vibe field is a physical potential field. It diffuses, advects, has gradients. Read it like weather, not like storage.
- **Cultural traditions aren't decoration.** They're different mathematical frameworks for the same truths. Use them when the Western lens isn't clicking for a user.
- **The intention runtime IS your job.** You decompose goals into intentions, assign to crew, verify conservation. That's the core loop.
