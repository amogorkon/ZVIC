

# Spec 02: SDFP Principles

## Definition

Signature-Driven Functional Programming (SDFP) in ZVIC is a paradigm where all functional code is governed by normalized, context-aware type signatures and protocol evidence, not by versioning or migration logic. SDFP is now strictly structural and context-driven.

## Core Principles

- **First-class, stateless functions:** All modules expose pure functions; no internal state is assumed or required.
- **Kind- and context-aware validation:** Compatibility is determined by kind signatures, type normalization, and contextual (static/dynamic) evidence.
- **Hot reload and dynamic adaptation:** Modules can be reloaded or swapped if and only if all type and protocol contracts are satisfied in the current context.
- **Declarative, explainable:** All compatibility and failure cases are explainable via evidence trees and error messaging.

## Use Cases

- Shared logic across microservices and distributed systems
- Safe, context-aware plugin/module reloads
- Real-time interface adaptation in agent-driven or dynamic environments
- Static and dynamic contract checking in CI, REPL, and runtime

## Benefits

- Predictable, explainable module behavior
- No version drift or migration overhead
- Rapid, safe iteration and deployment
- Full support for advanced type features (HKTs, protocols, partials)

---

See also: [Spec 01: Introduction](spec-01-Introduction.md), [Spec 03: ZVIC Contracts](spec-03-ZVIC-Contracts.md)
