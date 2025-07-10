
# ZVIC Compatibility Test Plan

## Purpose
This test plan focuses on verifying compatibility between two modules at all relevant levels: parameters, types, and constraints. Each section includes a test matrix to ensure all combinations are covered.


## 1. Parameter Signature Compatibility

Each matrix below describes compatibility between individual parameter signature shapes. If any one signature is incompatible, the entire module is considered incompatible.

✓ = Compatible (B can be safely used in place of A)
✗ = Incompatible (would cause some kind of Error)

### 1.1. Parameter Signature Shapes
We consider the following parameter shapes and test combinations within each category:

- Positional only
- Positional + keyword
- Keyword only
- Default values
- *args and **kwargs


### 1.2.1. Compatibility Matrix: Positional Only Signatures
Given Signature A with n  positional-only (and no other kinds of) arguments and Signature B with m arguments differing in different ways, we define compatibility as follows:

**Definitions:**
- required args = no default
- optional args = with default
- A_min = number of required args in A
- A_max = total number of positional args in A
- B_min = number of required args in B
- B_max = total number of positional args in B

**Compatibility rule:**
B is compatible with A if:
  `B_min <= A_min` and `B_max >= A_max`

| Scenario                                  |   Example                 |  Compatible?
|-------------------------------------------|---------------------------|--------
| Same parameters (names irrelevant)        | A(a,b,/) -> B(x, y,/)     | ✓
| Additional required args in B             | A(a, b,/) -> B(x, y, z,/) | ✗
| Fewer required args in B                  | A(a,b,/) -> B(x,/)        | ✗
| Additional optional params in B           | A(a,/) -> B(x, y=5,/)     | ✓
| Fewer optional args in B                  | A(a,b=1,/) -> B(x,/)      | ✗
| B has less required but more optional args | A(a, b,/) -> B(x, y=5, z=6/) | ✓
| A has less required args than B, same total | A(a, b=1,/) -> B(x, y,/) | ✗

Note: For positional-only signatures, compatibility requires that B has exactly as many positional arguments as A. Types need to be considered per argument - in a per-case basis, considered in its own compatibility matrix.


### 1.2.2. Compatibility Matrix: Positional & Keyword Signatures

**Definition:**
Given Signature A with n positional-or-keyword parameters (no / or *), and Signature B with m parameters of the same kind, we define compatibility as follows.

**Terminology:**
* required args = no default value
* optional args = have default values
* A_min = number of required args in A
* A_max = total number of args in A
* B_min = number of required args in B
* B_max = total number of args in B
* A_names, B_names = ordered list of parameter names in A and B

**Compatibility Conditions:**
    B is compatible with A iff:
    B_min ≤ A_min and B_max ≥ A_max
    A_names[:A_max] == B_names[:A_max]

(names must match in order up to the longest A signature)
Types (if present) must be compatible per-argument (deferred to a type matrix)

Compatibility Matrix:

| Scenario|	Example	|Compatible?
|---------------------------------------------------|---------------------------|-------------|
| Same args, same names	                            | A(a, b) -> B(a, b)                | ✓
| Same count, different names                       | A(a, b) -> B(x, y)	            | ✗
| Additional required args in B                     | A(a, b) -> B(a, b, c)	            | ✗
| Additional optional args in B                     | A(a, b) -> B(a, b, c=0)	        | ✓
| Fewer required args in B                          | A(a, b) -> B(a)	                | ✗
| Fewer total args in B                             | A(a, b=1, c=2) -> B(a, b=1)	    | ✗
| Fewer required, more optional                     | A(a, b, c=3) -> B(a, b=2, c=3)	| ✓
| Same names, reordered                             | A(a, b) -> B(b, a)	            | ✗
| A uses optional args, B requires them             | A(a, b=1) -> B(a, b)	            | ✗

**Key Differences from Positional-Only:**
* Names must match — unlike positional-only
* Reordering breaks compatibility — unlike keyword-only
* You can’t have extra required args in B
* You can have extra optional args in B (as long as name order matches)
* This form is most strict in terms of name and count alignment


### 1.2.3. Compatibility Matrix: Keyword Only Signatures

Given Signature A with n keyword-only parameters (after a / and *), and Signature B with m keyword-only parameters, we define compatibility as follows.

**Compatibility Conditions:**
    B is compatible with A iff:
    B_min ≤ A_min and B_max ≥ A_max
    A_names[:A_max] == B_names[:A_max]

(names must match in order up to the longest A signature)
Types (if present) must be compatible per-argument (deferred to a type matrix)


| Scenario                                  | Example                     | Compatible?
|-------------------------------------------|-----------------------------|-------------|
| Same args, same names                     | A(*, a, b) -> B(*, a, b)    | ✓
| Same count, different names               | A(*, a, b) -> B(*, x, y) | ✗
| Additional required args in B             | A(*, a, b) -> B(*, a, b, c) | ✗
| Additional optional args in B             | A(*, a, b) -> B(*, a, b, c=0) | ✓
| Fewer required args in B                  | A(*, a, b) -> B(*, a) | ✗
| Fewer total args in B                     | A(*, a, b=1, c=2) -> B(*, a, b=1) | ✗
| Fewer required, more optional             | A(*, a, b, c=3) -> B(*, a, b=2, c=3) | ✓
| Same names, reordered                     | A(*, a, b) -> B(*, b, a) | ✗
| A uses optional args, B requires them     | A(*, a, b=1) -> B(*, a, b) | ✗



### 1.2.4. Matrix: *args/**kwargs in Signatures
| Signature A \ Signature B | *args/**kwargs | No *args/**kwargs |
|--------------------------|----------------|-------------------|
| *args/**kwargs           | ✓              | ✓                 |
| No *args/**kwargs        | ✗              | ✓                 |
Note: Signature B can add *args/**kwargs for forward compatibility, but Signature A cannot require them if B does not provide.

---


## 2. Type Signature Compatibility

### 2.1. Type Signature Kinds
- Classic subclasses
- Abstract Base Classes (ABCs)
- Protocols
- Built-in types
- Custom classes
- Union types (e.g., int | str)
- Optional types (e.g., int | None)
- No type annotation

Each matrix below describes compatibility between individual type signatures (not whole modules).

### 2.2.1. Matrix: Classic Subclass Types
| Type A \ Type B | Classic subclass | Not subclass |
|-----------------|------------------|-------------|
| Classic subclass| ✓                | ✗           |
| Not subclass   | ✗                | ✗           |
Note: Only subclasses are compatible.

### 2.2.2. Matrix: ABC Types
| Type A \ Type B | ABC | Implements ABC | Not ABC |
|-----------------|-----|---------------|---------|
| ABC             | ✓   | ✓             | ✗       |
| Implements ABC  | ✓   | ✓             | ✗       |
| Not ABC         | ✗   | ✗             | ✗       |
Note: Must implement the required ABC interface.

### 2.2.3. Matrix: Protocol Types
| Type A \ Type B | Protocol | Implements Protocol | Not Protocol |
|-----------------|----------|--------------------|--------------|
| Protocol        | ✓        | ✓                  | ✗            |
| Implements Prot.| ✓        | ✓                  | ✗            |
| Not Protocol    | ✗        | ✗                  | ✗            |
Note: Must implement the required protocol.

### 2.2.4. Matrix: Built-in Types
| Type A \ Type B | Built-in | Not Built-in |
|-----------------|----------|--------------|
| Built-in        | ✓        | ✗            |
| Not Built-in    | ✗        | ✗            |
Note: Must match built-in type exactly.

### 2.2.5. Matrix: Union Types
| Type A \ Type B | Union | Member of Union | Not Member |
|-----------------|-------|-----------------|------------|
| Union           | ✓     | ✓               | ✗          |
| Member of Union | ✓     | ✓               | ✗          |
| Not Member      | ✗     | ✗               | ✗          |
Note: Type B must be a member of the union or the union itself.

### 2.2.6. Matrix: Optional Types
| Type A \ Type B | Optional | Not Optional |
|-----------------|----------|--------------|
| Optional        | ✓        | ✗            |
| Not Optional    | ✗        | ✓            |
Note: Optional is compatible with itself and with None.

---


## 3. Constraint Signature Compatibility

### 3.1. Constraint Signature Kinds
- No constraint
- Simple constraint (e.g., _ < 10)
- Multiple constraints (e.g., _ > 0 and _ < 10)
- Complex expressions (e.g., len(_) > 5)
- Placeholder usage (_)

Each matrix below describes compatibility between individual constraint signatures (not whole modules).

### 3.2.1. Matrix: No Constraint in Signatures
| Constraint A \ Constraint B | None | Any Constraint |
|----------------------------|------|----------------|
| None                       | ✓    | ✓              |
| Any Constraint             | ✗    | ✓              |
Note: Constraint B can add constraints, but cannot remove them if present in Constraint A.

### 3.2.2. Matrix: Simple vs. Multiple Constraints in Signatures
| Constraint A \ Constraint B | Simple | Multiple |
|----------------------------|--------|----------|
| Simple                     | ✓      | ✓        |
| Multiple                   | ✗      | ✓        |
Note: Constraint B can strengthen constraints, but not weaken them.

### 3.2.3. Matrix: Complex & Placeholder in Signatures
| Constraint A \ Constraint B | Complex | Placeholder |
|----------------------------|---------|-------------|
| Complex                    | ✓       | ✓           |
| Placeholder                | ✗       | ✓           |
Note: Placeholder is only compatible with itself or more restrictive constraints.

---

## 4. Combined Compatibility Scenarios

Test all combinations of parameter kinds, type kinds, and constraint kinds between Module A and Module B. This ensures that the compatibility logic is robust to all possible real-world and edge-case scenarios.

---

## 5. Edge Cases & Error Handling
- Missing or extra parameters
- Type mismatches
- Constraint mismatches
- Placeholder in unexpected positions
- Forward references and circular imports
- Unknown/unsupported types
- Robustness to invalid or missing annotations

---

## 6. Output & Reporting
- Canonicalization output is uniform and explicit
- Compatibility results are clear and actionable
- pprint_recursive output is validated for all scenarios

---

# End of Compatibility Test Plan
