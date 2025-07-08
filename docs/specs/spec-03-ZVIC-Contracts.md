

# Spec 03: ZVIC Contracts

## Definition

ZVIC Contracts are formal, migration-free interface contracts based on kind signatures, protocol coherence, and contextual evidence. All compatibility is structural and context-driven; versioning and migration are not supported or required.

## Core Principles

- **No versioning or migration:** All contracts are defined by current structure and context only.
- **Kind and protocol coherence:** Interface stability is enforced by kind signatures and trait-style protocol attribute ownership.
- **Contextual, explainable checks:** All contract checks are performed in a static or dynamic context, with full evidence and error reporting.
- **Partial and gradual typing:** Contracts support partial types and gradual evolution, with explicit evidence for unknowns.

## Benefits

- No dependency drift or legacy baggage
- Fully explainable, inspectable contracts and errors
- Safe, rapid evolution of interfaces and protocols

## Error Handling Example

When a contract check fails, a structured, explainable error is emitted:

```jsonc
{
  "error_id": "ZV5001",
  "type": "KindSignatureMismatch",
  "error_namespace": "ZVIC_CORE",
  "message": "Container kind mismatch: expected '* → *', actual '*'",
  "context": {
    "expected_kind": "* → *",
    "actual_kind": "*"
  },
  "evidence": {
    "rule": "HKT_KIND_MISMATCH",
    "expected": "* → *",
    "actual": "*"
  },
  "timestamp": "2025-07-08T00:00:00Z"
}
```

---

See also: [Spec 01: Introduction](spec-01-Introduction.md), [Spec 02: SDFP Principles](spec-02-SDFP-Principles.md)
