# ZVIC

Zero-Version Interface Contracts (ZVIC) is both a project and a paradigm for signature-based compatibility in Python modules. ZVIC enables safe, dynamic code reuse and interface stability without version numbers, using runtime verification of callable structure.

## Key Concepts

- **Signature-Driven Functional Programming (SDFP):** Treats function signatures as the primary interface contract. Modules expose only first-class, stateless functions. Compatibility is enforced by comparing function signatures.
- **Zero-Version Interface Contracts (ZVIC):** Manages code compatibility without version numbers, relying on signature hashes and runtime checks. Contracts are verified dynamically at runtime.

## Goals

- Eliminate the need for semantic versioning in shared code
- Enable safe, hot-reloadable modules
- Provide runtime guarantees for interface compatibility
- Facilitate rapid development and deployment cycles

## Canonicalization & Compatibility

Function signatures are canonicalized to ensure consistent interface identification and compatibility checks. See the [Canonicalization & Compatibility Spec](docs/specs/spec-04-Canonicalization-Compatibility.md) for details and compatibility rules.

## Error Handling

When a function signature changes incompatibly, ZVIC emits structured, machine-readable errors to support diagnostics and recovery.

## Project Structure

- `src/` - Main source code
- `tests/` - Test suite (unit, integration, TDD, quick tests)
- `docs/specs/` - Detailed specifications
- `pyproject.toml` - Build and packaging configuration
- `setup.py` - Minimal legacy packaging script

## Installation

```sh
pip install .
```

## Requirements
- Python 3.12+

## Further Reading

- [Spec 01: Introduction](docs/specs/spec-01-Introduction.md)
- [Spec 02: SDFP Principles](docs/specs/spec-02-SDFP-Principles.md)
- [Spec 03: ZVIC Contracts](docs/specs/spec-03-ZVIC-Contracts.md)
- [Spec 04: Canonicalization & Compatibility](docs/specs/spec-04-Canonicalization-Compatibility.md)

## Versioning Scheme

As of June 2025, ZVIC adopts a CalVer versioning scheme: `YYYY.0W[.patchx/devx/rcx]`, where:
- `YYYY` is the year
- `0W` is the zero-padded ISO week number
- Optional `.patchx`, `.devx`, `.rcx` for patches, dev, or release candidates

For example, `2025.26` corresponds to week 26 of 2025. This mirrors the structure of our Scrum logs (see `/docs/scrum/README.md`).

## License
MIT