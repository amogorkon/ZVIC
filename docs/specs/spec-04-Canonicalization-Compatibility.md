
# Spec 04: Canonicalization & Compatibility

## Canonicalization Strategy

Within the SDFP and ZVIC paradigms, function signatures are canonicalized to ensure consistent interface identification and compatibility checks. The canonical form is determined by parameter kind, name, type, and default value, following these rules:

| Parameter Kind           | Names Matter? | CID Determined By           | Compatible on Name Change? | Compatible on Type Change? | Compatible on Default Change? |
|-------------------------|:-------------:|-----------------------------|:--------------------------:|:--------------------------:|:-----------------------------:|
| Positional-only         | No            | Order + Types               | ✅ Yes                     | ❌ No                      | N/A                           |
| Positional-or-keyword   | Yes           | Names + Types + Defaults    | ❌ No                      | ❌ No                      | ❌ No                         |
| Keyword-only            | Yes           | Names + Types + Defaults    | ❌ No                      | ❌ No                      | ❌ No                         |
| *args                   | No            | Type                        | ✅ Yes                     | ❌ No                      | N/A                           |
| **kwargs                | No            | Type                        | ✅ Yes                     | ❌ No                      | N/A                           |

*Adding an optional positional-or-keyword parameter is compatible only if it has a default value.*

## Canonical Representation Examples

| Function Definition | Canonical Representation |
|---------------------|-------------------------|
| `def process(a: int, b: int, /) -> float:` | `{ "name": "process", "params": [ {"kind": "POSITIONAL_ONLY", "type": "int"}, {"kind": "POSITIONAL_ONLY", "type": "int"} ], "return": "float" }` |
| `def transform(data: dict, verbose: bool = False) -> list:` | `{ "name": "transform", "params": [ {"kind": "POSITIONAL_OR_KEYWORD", "name": "data", "type": "dict"}, {"kind": "POSITIONAL_OR_KEYWORD", "name": "verbose", "type": "bool", "default": "False"} ], "return": "list" }` |
| `def render(*, width: int, height: int) -> Image:` | `{ "name": "render", "params": [ {"kind": "KEYWORD_ONLY", "name": "width", "type": "int"}, {"kind": "KEYWORD_ONLY", "name": "height", "type": "int"} ], "return": "Image" }` |

## Compatibility Matrix

| Change Type                | Positional-only | Positional-or-keyword | Keyword-only |
|----------------------------|:--------------:|:---------------------:|:------------:|
| Name change                | ✅ Yes         | ❌ No                 | ❌ No        |
| Type change                | ❌ No          | ❌ No                 | ❌ No        |
| Default value change       | N/A            | ❌ No                 | ❌ No        |
| Add optional param         | N/A            | ✅ Yes*               | ❌ No        |
| Add required param         | ❌ No          | ❌ No                 | ❌ No        |

*Only compatible if new parameter has a default value*

---

See also: [Spec 01: Introduction](spec-01-Introduction.md), [Spec 02: SDFP Principles](spec-02-SDFP-Principles.md), [Spec 03: ZVIC Contracts](spec-03-ZVIC-Contracts.md)
