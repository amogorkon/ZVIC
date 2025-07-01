
# Spec 02: SDFP Principles

## Definition

Signature-Driven Functional Programming (SDFP) is a runtime programming paradigm where the behavior and lifecycle of functional code is governed by the structure of its function signatures, not by external configuration or versioning. SDFP is a paradigm, not a specific implementation.


## Core Principles

- **First-class functions only**: Modules should expose functions without internal state.
- **Signature-centric validation**: Compatibility is enforced by comparing function signatures (e.g., via `inspect.signature()` in Python).
- **Hot reload enforcement**: Modules can be reloaded safely if all signatures remain compatible.
- **Declarative, observable**: Runtime code behavior is inspectable and predictable.


## Use Cases

- Shared logic across microservices
- Safe plugin/module reloads in development and production
- Real-time interface adaptation in agent-assisted systems


## Benefits

- Predictable module behavior
- Reduced risk of runtime errors due to interface drift
- Enables rapid iteration and deployment

---

See also: [Spec 01: Introduction](spec-01-Introduction.md), [Spec 03: ZVIC Contracts](spec-03-ZVIC-Contracts.md)
