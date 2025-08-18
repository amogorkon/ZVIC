# CHANGELOG

All notable changes to this project are documented in this file.

## [2025.34] - 2025-08-18

### Fixed
- Fixed several compatibility/introspection edge cases where `inspect.signature()` would fail on descriptors by unwrapping `staticmethod`/`classmethod` to their underlying functions.
- Resolved multiple false-positive or noisy debug prints by switching to `logging.debug` and clearer messages.
- Addressed a number of linter/typing issues across `src/zvic` (minor refactors and naming fixes) to reduce warnings and make the codebase easier to maintain.

### Specs implemented (summary checklist)
The following specification documents are implemented or reflected by this release:

- [x] Spec 02: SDFP Principles (docs/specs/spec-02-SDFP-Principles.md)
- [x] Spec 03: ZVIC Contracts (docs/specs/spec-03-ZVIC-Contracts.md)
- [x] Spec 04: Canonicalization & Compatibility (docs/specs/spec-04-Canonicalization-Compatibility.md)
- [x] Spec 07: Annotation Constraints & Rewriting (docs/specs/spec-07-Annotation-Constraints.md)
- [x] Spec 08: Compatibility (docs/specs/spec-08-Compatibility.md)

### Tests
- All unit tests pass: `pytest` reported 92 passed at the time of this release candidate.