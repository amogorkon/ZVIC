# LLM-Focused Summary: ZVIC (Zero-Version Interface Contracts)

This document provides a concise, LLM-oriented summary of ZVIC: both the project and the paradigm of Zero-Version Interface Contracts. ZVIC is a project that enables and enforces the ZVIC paradigm. This summary is intended to help LLMs understand, reason about, and generate code or documentation that aligns with these principles and requirements.

## What is ZVIC?

ZVIC is both a project and a paradigm for safe, dynamic code reuse in distributed Python systems. As a project, ZVIC implements and enforces the Zero-Version Interface Contracts paradigm.

## ZVIC: Project and Paradigm

- Eliminates the need for semantic versioning.
- Interface stability is ensured through signature hashes and runtime checks.
- Contracts are verified dynamically at runtime, not by version numbers.
- Fail-fast: incompatible changes are detected and reported immediately.
- ZVIC (the project) provides tools and runtime enforcement for the ZVIC paradigm.

## Key Requirements

- No semantic versioning: ZVIC avoids version numbers for interface compatibility.
- Signature-based compatibility: ZVIC relies on function signatures as the primary contract.
- Runtime contract validation: ZVIC performs runtime checks to ensure interface compatibility.
- Human-friendly diagnostics: ZVIC provides clear, structured error messages for compatibility issues.
- Project ZVIC provides practical enforcement and tooling for these requirements.

## Core Definitions

- **Signature-Driven Functional Programming (SDFP):** A runtime programming paradigm where the behavior and lifecycle of functional code is governed by the structure of its function signatures, not by external configuration or versioning. SDFP is a paradigm, not a specific implementation. Its core principles are: first-class functions only, signature-centric validation, hot reload enforcement, and declarative, observable code behavior.
- **Zero-Version Interface Contracts (ZVIC):** Both a project and a paradigm for managing compatibility by verifying callable structure at runtime, not by version numbers. The ZVIC project implements and enforces this paradigm in distributed Python systems.

## Guidance: How to Reason About ZVIC

- When generating or refactoring code, always preserve function signatures for compatibility.
- Avoid introducing stateful modules or relying on version numbers for interface management.
- Use signature inspection and hashing to validate compatibility.
- When documenting or suggesting changes, highlight signature changes and their impact on compatibility.
- For error handling, prefer structured, machine-readable diagnostics (e.g., JSON error objects).

## Where to Find More Details

| Topic                | Spec Section                                  |
|----------------------|-----------------------------------------------|
| SDFP Principles      | [specs/spec-02-SDFP-Principles.md](specs/spec-02-SDFP-Principles.md) |
| ZVIC Contracts       | [specs/spec-03-ZVIC-Contracts.md](specs/spec-03-ZVIC-Contracts.md)   |
| Canonicalization     | [specs/spec-04-Canonicalization-Compatibility.md](specs/spec-04-Canonicalization-Compatibility.md) |
| Error Handling       | [specs/spec-03-ZVIC-Contracts.md](specs/spec-03-ZVIC-Contracts.md)   |
| Migration Tooling    | [specs/spec-04-Canonicalization-Compatibility.md](specs/spec-04-Canonicalization-Compatibility.md) |

---

> Function and class signatures should be treated as the source of truth for compatibility and interface reasoning. Version numbers are not relevant; structure and runtime validation are paramount.
