
# Spec 03: ZVIC Contracts

## Definition

Zero-Version Interface Contracts (ZVIC) is a paradigm for managing code compatibility without version numbers, relying on runtime verification of callable structure. ZVIC is a paradigm, not a specific implementation. The JustUse project applies this paradigm to real-world systems.


## Core Principles

- **No semantic versioning required**
- **Interface stability through signature hashes**
- **Runtime fail-fast checks on API shape**
- **Inter-module contracts verified dynamically**


## Benefits

- No dependency version drift
- Hashable, inspectable contracts
- Ideal for fast-moving, high-trust teams


## Error Handling Example

When a function signature changes incompatibly, a structured error is emitted:

```jsonc
{
  "error_id": "JU3010",
  "type": "SignatureMismatchError",
  "error_namespace": "JUSTUSE_RELOADER",
  "message": "Function 'parse_order' signature changed incompatibly",
  "context": {
    "function": "parse_order",
    "old_signature": "parse_order(data: dict) -> Order",
    "new_signature": "parse_order(data: dict, *, flags: int = 0) -> Order"
  },
  "recovery_actions": [
    {
      "type": "manual_review",
      "description": "Check if new optional args are backwards compatible"
    }
  ],
  "justuse_version": "0.8.2",
  "timestamp": "2025-06-21T22:14:59Z"
}
```

---

See also: [Spec 01: Introduction](spec-01-Introduction.md), [Spec 02: SDFP Principles](spec-02-SDFP-Principles.md)
