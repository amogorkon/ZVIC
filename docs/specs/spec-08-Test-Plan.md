
# ZVIC Compatibility Test Plan

## Purpose
This test plan focuses on verifying compatibility between two modules at all relevant levels: parameters, types, and constraints. Each section includes a test matrix to ensure all combinations are covered.

All cases are numbered for easy reference within test cases. First column of each matrix is `ID` which is used to reference the specific case in test cases.

## 1. Parameter Signature Compatibility

Each matrix below describes compatibility between individual parameter signature shapes. If any one signature is incompatible, the entire module is considered incompatible.


**Terminology:**
* required args = no default value
* optional args = have default values
* A_min = number of required args in A
* A_max = total number of args in A
* B_min = number of required args in B
* B_max = total number of args in B
* A_names, B_names = ordered list of parameter names in A and B
* ✓ = Compatible (B can be safely used in place of A)
* ✗ = Incompatible (would cause some kind of Error)

### 1.1. Parameter Signature Shapes
We consider the following parameter shapes and test combinations within each category:

- Positional only (before `/`)
- Positional & keyword (between `/` and `*`)
- Keyword only (after `*`)
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

**Compatibility Condition:**
B is compatible with A iff:

    `B_min <= A_min` and `B_max >= A_max`

| ID | Scenario                                 |   Example                 |  Compatible?
|----|-------------------------------------------|---------------------------|--------
| P1| Same parameters (names irrelevant)        | A(a,b,/) => B(x, y,/)     | ✓
| P2| Additional required args in B             | A(a, b,/) => B(x, y, z,/) | ✗
| P3| Fewer required args in B                  | A(a,b,/) => B(x,/)        | ✗
| P4| Additional optional params in B           | A(a,/) => B(x, y=5,/)     | ✓
| P5| Fewer optional args in B                  | A(a,b=1,/) => B(x,/)      | ✗
| P6| B has less required but more optional args | A(a, b,/) => B(x, y=5, z=6/) | ✓
| P7| A has less required args than B, same total | A(a, b=1,/) => B(x, y,/) | ✗

Note: For positional-only signatures, compatibility requires that B has exactly as many positional arguments as A. Types need to be considered per argument - in a per-case basis, considered in its own compatibility matrix.


### 1.2.2. Compatibility Matrix: Positional & Keyword Signatures

**Definition:**
Given Signature A with n positional-or-keyword parameters (between `/` and `*`), and Signature B with m parameters of the same kind, we define compatibility as follows.


**Compatibility Conditions:**
B is compatible with A iff:

    B_min ≤ A_min and B_max ≥ A_max

    Required parameters: A_names[0:A_min] == B_names[0:A_min]
    (Exact name/order match for required args)

    Optional parameters: A_names[A_min:A_max] == B_names[A_min:A_max]
    (Exact name/order match for optional args)

    New parameters: B_names[A_max:B_max] can be any names
    (Since they'll always use defaults)

(names must match in order up to the longest A signature)
Types (if present) must be compatible per-argument (deferred to a type matrix)

Compatibility Matrix:

| ID | Scenario|	Example	|Compatible?
|----|-----------------------------------------------|---------------------------|-------------|
|PK1| Same args, same names	                            | A(a, b) => B(a, b)                | ✓
|PK2| Same count, different names                       | A(a, b) => B(x, y)	            | ✗
|PK3| Additional required args in B                     | A(a, b) => B(a, b, c)	            | ✗
|PK4| Additional optional args in B                     | A(a, b) => B(a, b, c=0)	        | ✓
|PK5| Fewer required args in B                          | A(a, b) => B(a)	                | ✗
|PK6| Fewer total args in B                             | A(a, b=1, c=2) => B(a, b=1)	    | ✗
|PK7| Fewer required, more optional                     | A(a, b, c=3) => B(a, b=2, c=3)	| ✓
|PK8| Same names, reordered                             | A(a, b) => B(b, a)	            | ✗
|PK9| A uses optional args, B requires them             | A(a, b=1) => B(a, b)	            | ✗

**Key Differences from Positional-Only:**
* Names must match — unlike positional-only
* Reordering breaks compatibility — unlike keyword-only
* You can’t have extra required args in B
* You can have extra optional args in B (as long as name order matches)
* This form is most strict in terms of name and count alignment


### 1.2.3. Compatibility Matrix: Keyword Only Signatures

Given Signature A with n keyword-only parameters (after *), and Signature B with m keyword-only parameters, we define compatibility as follows.

**Compatibility Conditions:**

B is compatible with A if all the following hold:

    B_min ≤ A_min (B requires no more parameters than A)
    B_max ≥ A_max (B accepts at least as many parameters as A)
    A_names ⊆ B_names (every name A accepts must also be accepted by B; extra names in B are allowed)
    Every extra parameter in B (i.e. names in B_names − A_names) is optional


| ID | Scenario                                  | Example                     | Compatible?
|----|-----------------------------------------------|-----------------------------|-------------|
|K1| Same args, same names                     | A(*, a, b) => B(*, a, b)      | ✓
|K2| Same count, different names               | A(*, a, b) => B(*, x, y)      | ✗
|K3| Additional required args in B             | A(*, a, b) => B(*, a, b, c)   | ✗
|K4| Additional optional args in B             | A(*, a, b) => B(*, a, b, c=0) | ✓
|K5| Fewer required args in B                  | A(*, a, b) => B(*, a)         | ✗
|K6| Fewer total args in B                     | A(*, a, b=1, c=2) => B(*, a, b=1) | ✗
|K7| Fewer required, more optional             | A(*, a, b, c=3) => B(*, a, b=2, c=3) | ✓
|K8| Same names, reordered                     | A(*, a, b) => B(*, b, a)      | ✓
|K9| A uses optional args, B requires them     | A(*, a, b=1) => B(*, a, b)    | ✗



### 1.2.4. Compatibility Matrix: *args/**kwargs with Positional Only

**Structural Compatibility Conditions**

Let

* A_max = n (number of positional-only args A takes)
* B_prefix_req = count of fixed parameters in B that have no default
* B_prefix_count = total fixed positional parameters in B (required + optional)
* B_has_varargs = whether B declares *args
* B_has_varkw = whether B declares **kwargs

Then B is structurally compatible with A iff:

1. B_prefix_req ≤ A_max (B does not require more positional args than A will ever pass)

2. Either
* B_has_varargs, or
* B_prefix_count ≥ A_max (B can absorb all A’s positional args, via *args or an equal-or-longer fixed prefix)

3. B does not introduce any required keyword-only parameters (A never passes keywords) (You may add keyword-only params only if they have defaults, or use **kwargs)

| ID  | Scenario       | Example                                          | Compatible? | Reasoning
|-----|----------------|--------------------------------------------------|-------------|----------
|AP1|	*args only|	A(a, b, /) → B(*args)                                 | ✓           | 0 ≤ 2 + *args handles positions
|AP2|	*args + prefix|	A(a, b, /) → B(x, *args)                          |	✓           | 1 ≤ 2 + *args handles overflow
|AP3|	**kwargs only|	A(a, b, /) → B(**kwargs)                          |	✗           | No *args + 0 < 2
|AP4|	*args + **kwargs|	A(a, b, /) → B(*args, **kwargs)               |	✓           | 0 ≤ 2 + *args handles positions
|AP5|	Insufficient fixed + **kwargs|	A(a, b, /) → B(a=1, **kwargs)     |	✗           | No *args + 1 < 2
|AP6|	Optional keyword-only alone|	A(a, b, /) → B(*, k=5)            |	✗           | No *args + 0 < 2
|AP7|	Required keyword-only|	A(a, b, /) → B(*args, k)                  |	✗           | Required keyword-only k
|AP8|	Fixed params match A_max|	A(a, b, /) → B(x, y)                  |	✓           | 2 ≤ 2 + 2 ≥ 2
|AP9|	Optional params + **kwargs|	A(a, b, /) → B(x, y=1, **kwargs)      |	✓           | 1 ≤ 2 + 2 ≥ 2
|AP10|	✓ Optional keyword-only + *args|	A(a, b, /) → B(*args, k=5)    |	✓           |  0 ≤ 2 + *args handles positions
|AP11|	✓ Zero args evolution|	A() → B(*, k=5)                           |	✓           | A_max=0, 0 ≥ 0

### 1.2.5. Compatibility Matrix: *args/**kwargs with Positional & Keyword

|ID | Scenario       | Example                                            | Compatible? | Reasoning
|-----|----------------|--------------------------------------------------|-------------|----------
|APK1|	*args only|	A(a, b) → B(*args)                                    |  X	        | Fails keyword calls: A(a=1,b=2) → B(a=1,b=2) raises TypeError (unexpected keyword)
|APK2|	*args + prefix|	A(a, b) → B(x, *args)                             |	X           | Fails keyword calls: A(a=1,b=2) → B(x=1,b=2) fails (b unexpected)
|APK3|	**kwargs only|	A(a, b) → B(**kwargs)|    ✗| Fails positional calls: A(1,2) → B(1,2) raises TypeError
|APK4|	*args + **kwargs|	A(a, b) → B(*args, **kwargs)|	✓|	0 ≤ 2 & *args handles positions
|APK5|	Insufficient fixed + **kwargs|	A(a, b) → B(a=1, **kwargs)|	✗|	No *args & 1 < 2
|APK6|	Required keyword-only|	A(a, b) → B(*args, k)  |	✗|	Required keyword-only k
|APK7|	Optional params + **kwargs|	A(a, b) → B(x, y=1, **kwargs)|	X|	1 ≤ 2 & 2 ≥ 2, but fails keyword calls: A(a=1,b=2) → B(a=1,b=2) raises TypeError: B() missing 1 required positional argument: 'x'
|APK8|	Optional keyword-only + *args|	A(a, b) → B(*args, k=5)|	X|	0 ≤ 2 & *args handles positions but kwargs of A are not handled

If B removes *args or **kwargs that A had, it cannot accept the same variety of calls, and thus breaks compatibility.

### 1.2.6. Compatibility Matrix: *args/**kwargs with Keyword Only

Assume Signature A is: A(*, a, b) — i.e., it accepts keyword-only a and b.



| ID |	Scenario |B Signature|	Compatible?|	Reasoning
|----|-----------|------------------------------------|---------------------------|-------------|
|AK1|	*args only	|(*args)	|✗|	B rejects keyword arguments a and b.
|AK2|	Fixed param + *args|	(x, *args)	|✗|	B requires x (not in A), and doesn’t accept a, b.
|AK3|	**kwargs only	|(**kwargs)	|✓|	**kwargs catches all keywords a, b.
|AK4|	*args, **kwargs	|(*args, **kwargs)	|✓|	**kwargs absorbs keywords; *args is irrelevant.
|AK5|	Declares a, plus **kwargs|	(a=1, **kwargs)	|✓|	B declares a, and **kwargs absorbs b.
|AK6|	Adds required kw-only param|	(*args, k)	|✗|	k is required but not supplied by A.
|AK7|	Fixed param not in A|	(x, y=1, **kwargs)	|✗|	B requires x, which A does not provide.
|AK8|	Optional kw-only + *args|	(*args, k=5)	|✗|	No **kwargs to catch a, b; k is unused.

### 1.2.7. Transition Rules between Kinds of Parameters

The only safe transition is from positional-only or keyword-only to positional & keyword as it maintains the rules for either positional or keyword parameters while adding capabilities for either kind of parameters, requiring stricter rules either regarding positioning or naming of arguments.
A transition from positional & keyword to positional-only or keyword-only would require extra tests on the caller's side to ensure that the caller does not pass arguments that would violate the rules of positional-only or keyword-only parameters (e.g. passing an argument as positional with unexpected keyword arguments).


## 2. Parameter Compatibility

### 2.1. Parameter categories
- Classic subclasses
- Abstract Base Classes (ABCs)
- Protocols
- Built-in types
- Custom classes
- Union types (e.g., int | str)
- Optional types (e.g., int | None)
- No type annotation

**Important Note:**
Especially tricky is the move from no type annotation or Any to a specific type, as it inevitably breaks compatibility if the caller passes a type that is not compatible with the new type signature. However, this is exactly what Python encourages by its design of Optional Typing, which is in direct conflict of the idea of zero-versioning compatibility. Therefor it is recommended to follow the idea of Optional Typing at first (no type annotations or very generic types) but then make a hard transition to fully specified type signatures (as a baseline commit) and then go from there. **Every time a relaxed type is tightened, it is a breaking change that requires a new baseline commit.**

**Note on Type Transitioning:**
Transitioning between types is tricky. While theoretically widening the type may seems compatible at first glance, in practice this can lead to runtime errors. Instead of directly moving from A: Dog => B: Animal in order to accommodate another C: Cat type, it is recommended to first move to B: Dog | Cat | Animal and go from there. This way we get a temporal decoupling, allowing some deprecation (with warnings, tests, dispatch etc.) before the final transition to B: Animal or possible B: AnimalProtocol (which would be the most flexible solution).

### 2.2. Compatibility Matrix: Type Signatures

| ID | Scenario | Example | Compatible? | Revised Reasoning
|----|-----------------------------------------------|---------------------------|-------------|----------------
| T0 | Untyped/Any → Specific type | A: Any → B: int | ✗ | Type constraint added
| T1 | Same type | A: int → B: int | ✓ | Exact match
| T2 | Base → Derived (narrowing) | A: Animal → B: Cat | ✗ | New function requires specific subtype
| T3 | Interface → Concrete | A: Sized → B: list | ✗ | Implementation restricts valid inputs
| T4 | Type → Wider union | A: int → B: int|str | ✓ | Accepts original type + more
| T5 | Required → Optional | A: int → B: int|None | ✓ | Original callers already pass required type
| T6 | Implicit conversion | A: int → B: float | ✗ | No explicit subtype relationship
| T7 | ABC hierarchy | A: Integral → B: Real | ✓ | Explicit subtyping via ABCs
| T8 | Adjacent types | A: uint8 → B: uint16 | ✗ | Behavioral differences matter
| T9 | Derived → Base (widening) | A: Cat → B: Animal | ✓ | Contravariant parameter acceptance
| T10 | Container invariance | A: list[int] → B: list[str] | ✗ | Generic parameters invariant
| T11 | Container contravariance | A: list[Dog] → B: list[Animal] | ✓ | List of Dog is compatible with list of Animal
| T12 | Function => Callable Class/Instance | A: def foo(x: int) => B: class Foo with def __call__(x: int) | ✓ | Callable class can be used as a function, widening options
| T13 | Callable Class => Function | A: class Foo with def __call__(x: int) => B: def foo(x: int) | ✗ | Function is more limited than callable class, narrowing
| T14 | Attribute => Property | A: Foo.a => B: Foo.a (property for read, write and del) | ✓ | Property is equivalent to attribute if ALL THREE operations are supported
| T15 | Attribute => Read-Only Property | A: Foo.a => B: Foo.a (property for read only) | ✗ | Read-only property is narrower than attribute, breaking compatibility
| T16 | Read-Only Property => Attribute | A: Foo.a (property for read only) => B: Foo.a | ✓ | Read-only property can be used as an attribute, widening options
| T17 | Read-Only Property => Read-Write Property | A: Foo.a (property for read only) => B: Foo.a (property for read, write and del) | ✓ | Read-only property can be used as a read-write property, widening
| T18 | Read-Write Property => Read-Only Property | A: Foo.a (property for read, write and del) => B: Foo.a (property for read only) | ✗ | Read-write property is wider than read-only property, breaking compatibility
| T19 | Function never raises => Function may raise  OR Function may raise => Function never raises | A: def foo(x: int) -> int => B: def foo(x: int) -> int & possible Exception | ✗ | Raising OR NOT raising an exception is part of the function's contract - it cannot be changed without breaking compatibility as others may rely on this behaviour.
---


## 3. Constraint Signature Compatibility

### 3.1. Constraint Signature Kinds
**Currently not tested against**
- No constraint
- Simple constraint (e.g., _ < 10)
- Multiple constraints (e.g., _ > 0 and _ < 10)
- Complex expressions (e.g., len(_) > 5)
- Placeholder usage (_)


| ID | Scenario | Example | Compatible? | Reasoning
|----|----------|---------|-------------|----------------
| C0a | No constraint in A, no constraint in B | A(a:int) => B(a:int) | ✓ | No constraints to break compatibility
| C0b | same constraint in A and B | A(a:int(_ <10)) => B(a:int(_ <10)) | ✓ | Exact match, no issues
| C1 | No constraint in A, any in B | A(a:int) => B(a:int(_ <20)) | ✗ | passing anything to A outside constraints will break B
| C2 | Any constraint in A, no constraint in B | A(a:int(_ <10)) => B(a:int) | ✓ | No constraints in B, so A can pass anything
| C3 | wider constraint in B | A(a:int(_ <10)) => B(a:int(_<20)) | ✓ | B accepts more than A, so A can pass anything
| C4 | narrower constraint in B | A(a:int( _ <20)) => B(a:int(_ <10)) | ✗ | some inputs that A accepts will not be accepted by B


# 4. Module/Interface Compatibility (Mx)

## 4.1. Interface as Set of Callables

For module or class compatibility, the interface is defined as the set of all callable attributes (functions, methods, __init__, __call__, etc.) exposed by the module/class. For B to be compatible with A, every callable present in A must exist in B with a compatible signature. B may have additional callables, but must not remove or break any callable present in A.

**Compatibility Condition:**

    The set of callable names in B must be a superset of A's, and for every callable in A, the signature in B must be compatible (per the rules in Chapters 1–3).

If B is missing any callable that A exposes, or if any callable's signature is incompatible, then B is not compatible with A.

## 4.2. Module Compatibility Scenarios

| ID  | Scenario        | Example                | Compatible? | Reasoning |
|-----|-----------------|------------------------|-------------|-----------|
| M1  | B adds a new callable                    | A: foo, bar → B: foo, bar, baz           | ✓           | Addition is safe; callers using A are unaffected |
| M2  | B removes a callable present in A        | A: foo, bar → B: foo                     | ✗           | Removal breaks callers relying on bar |
| M3 | B changes a sync def to async def and vice versa | A: foo(x: int) => B: async foo(x: int) | ✗ | Async def cannot be used in place of sync def, breaking caller expectations |
| M4 | B converts a function to a generator by using yield | A: foo(x: int) => B: foo(x: int) | ✗ | Generator cannot be used in place of regular function, breaking caller expectations |
| M5 | Removing attributes, constants or classes in B that were present in A | A: foo, bar, Baz → B: foo, Baz | ✗ | Removal of any attribute breaks compatibility as callers may expect it to exist |
| M6 | Removing items that are designated private | A: _foo, _bar → B: _foo | ✓ | Private items can be removed without breaking compatibility |
| M7 | Removing items from __all__ | A: __all__ = [foo, bar] → B: __all__ = [foo] | ✗ | Removal from __all__ breaks compatibility as it changes the public API |
| M8 | Adding items to an Enum | A: Color.RED, Color.GREEN → B: Color.RED, Color.GREEN, Color.BLUE | ✓ | Adding to an Enum is safe; callers using A are unaffected |
| M9 | Removing items from an Enum | A: Color.RED, Color.GREEN → B: Color.RED | ✗ | Removal from an Enum breaks compatibility as it changes the set of valid values |
| M10 | Changing the order of an Enum | A: Color.RED, Color.GREEN, Color.BLUE → B: Color.GREEN, Color.RED, Color.BLUE | ✗ | Changing the order of Enum members breaks compatibility as it changes the meaning of the values |

**Note:** This approach treats the set of callables as the module/class interface. Compatibility is only preserved if B's callable set is a superset of A's, and all signatures are compatible.