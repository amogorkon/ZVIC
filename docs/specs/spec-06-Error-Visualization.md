# ZVIC Contract Diff Visualization: Design & Implementation

Based on your insight that diff visualization is crucial for compatibility analysis, I'll design a comprehensive visualization system that integrates directly with ZVIC's compatibility reports.

## Core Visualization Components

### 1. Multi-Level Diff Representation

```python
def visualize_diff(compatibility_report: dict, detail_level: str = "summary") -> str:
    """
    Generate visual diff based on compatibility report
    :param detail_level: 'summary' | 'function' | 'parameter'
    """
    output = []

    # Summary visualization
    if detail_level == "summary":
        output.append(f"## Contract Compatibility Summary")
        output.append(f"🟢 Compatible: {len(compatibility_report['compatible']} items")
        output.append(f"🔴 Breaking: {len(compatibility_report['breaking'])} changes")
        output.append(f"🟡 Warnings: {len(compatibility_report['warnings'])}")
        output.append("```mermaid\npie showData\n    title Change Distribution\n    \"Compatible\" : {compatible}\n    \"Breaking\" : {breaking}\n    \"Warnings\" : {warnings}\n```")

    # Function-level diff
    elif detail_level == "function":
        for item in compatibility_report['diffs']:
            if item['change_type'] == 'removed':
                output.append(f"### ❌ Removed: {item['name']}")
                output.append(f"```diff\n- {item['old_signature']}\n```")
            elif item['change_type'] == 'added':
                output.append(f"### ⭐ Added: {item['name']}")
                output.append(f"```diff\n+ {item['new_signature']}\n```")
            elif item['change_type'] == 'modified':
                output.append(f"### 🔄 Modified: {item['name']}")
                output.append(render_signature_diff(item['old_signature'], item['new_signature']))

    # Parameter-level diff
    elif detail_level == "parameter":
        for item in compatibility_report['diffs']:
            if item['change_type'] == 'modified':
                output.append(f"### 🔍 {item['name']} Parameter Changes")
                output.append(render_parameter_diff(item['param_diffs']))

    return "\n".join(output)

def render_signature_diff(old_sig: dict, new_sig: dict) -> str:
    """Visualize function signature differences"""
    diff = []
    # Function name
    if old_sig['name'] != new_sig['name']:
        diff.append(f"- Name: {old_sig['name']} → {new_sig['name']}")

    # Parameters
    param_lines = []
    for i in range(max(len(old_sig['params']), len(new_sig['params']))):
        old_param = old_sig['params'][i] if i < len(old_sig['params']) else None
        new_param = new_sig['params'][i] if i < len(new_sig['params']) else None

        if not old_param:
            param_lines.append(f"+ [New] {format_param(new_param)}")
        elif not new_param:
            param_lines.append(f"- [Removed] {format_param(old_param)}")
        elif old_param != new_param:
            param_lines.append(f"~ [Changed] {format_param(old_param)} → {format_param(new_param)}")
        else:
            param_lines.append(f"  {format_param(old_param)}")

    diff.append("Parameters:")
    diff.append("```diff\n" + "\n".join(param_lines) + "\n```")

    # Return type
    if old_sig['return'] != new_sig['return']:
        diff.append(f"- Return: {old_sig['return']} → {new_sig['return']}")

    return "\n".join(diff)
```

### 2. Schema Visualization System

```python
def visualize_schema_diff(old_schema: dict, new_schema: dict) -> str:
    """Visualize complex schema differences (enums, dataclasses)"""
    output = []

    # Enum visualization
    if old_schema.get('type') == 'enum':
        output.append(f"## Enum: {old_schema['name']}")
        table = [
            "| Member | Old Value | New Value | Status |",
            "|--------|-----------|-----------|--------|"
        ]

        old_members = {m['name']: m['value'] for m in old_schema['members']}
        new_members = {m['name']: m['value'] for m in new_schema['members']}

        all_members = set(old_members.keys()) | set(new_members.keys())
        for member in sorted(all_members):
            old_val = old_members.get(member, "❌")
            new_val = new_members.get(member, "❌")

            if member not in new_members:
                status = "🔴 Removed"
            elif member not in old_members:
                status = "🟢 Added"
            elif old_val != new_val:
                status = "🟠 Changed"
            else:
                status = "⚪ Unchanged"

            table.append(f"| {member} | {old_val} | {new_val} | {status} |")

        output.append("\n".join(table))

    # Dataclass visualization
    elif old_schema.get('type') == 'dataclass':
        output.append(f"## Dataclass: {old_schema['name']}")
        output.append("```mermaid\nclassDiagram")
        output.append(f"  class {old_schema['name']} {{")

        # Field comparison
        old_fields = {f['name']: f for f in old_schema['fields']}
        new_fields = {f['name']: f for f in new_schema['fields']}
        all_fields = set(old_fields.keys()) | set(new_fields.keys())

        for field in sorted(all_fields):
            old_f = old_fields.get(field)
            new_f = new_fields.get(field)

            if not new_f:
                output.append(f"    ~~{field}~~ : {old_f['type']}  // Removed")
            elif not old_f:
                output.append(f"    +{field} : {new_f['type']}  // Added")
            else:
                changes = []
                if old_f['type'] != new_f['type']:
                    changes.append(f"type: {old_f['type']}→{new_f['type']}")
                if old_f.get('default') != new_f.get('default'):
                    changes.append("default changed")

                if changes:
                    output.append(f"    ~{field} : {new_f['type']}  // {', '.join(changes)}")
                else:
                    output.append(f"    {field} : {new_f['type']}")

        output.append("  }\n```")

    return "\n".join(output)
```

### 3. Impact Analysis Visualization

```python
def visualize_impact(compatibility_report: dict) -> str:
    """Show dependency graph of breaking changes"""
    output = ["## Impact Analysis"]
    output.append("```mermaid\ngraph TD")

    # Node definitions
    for item in compatibility_report['breaking']:
        output.append(f"  {item['id']}[{item['name']}]:::breaking")

    for item in compatibility_report['warnings']:
        output.append(f"  {item['id']}[{item['name']}]:::warning")

    # Dependency relationships
    for item in compatibility_report['dependencies']:
        output.append(f"  {item['source']} --> {item['target']}")

    # Styling
    output.append("""
  classDef breaking fill:#ffcccc,stroke:#ff0000
  classDef warning fill:#ffffcc,stroke:#ffcc00
  classDef normal fill:#ccffcc,stroke:#00cc00
    """)
    output.append("```")

    # Affected consumers
    if compatibility_report.get('consumers'):
        output.append("\n### Affected Consumers")
        for consumer in compatibility_report['consumers']:
            output.append(f"- {consumer['service']} ({consumer['endpoint']})")

    return "\n".join(output)
```

## Enhanced Compatibility Reporting

### 1. Augmented Compatibility Report Structure

```python
def generate_compatibility_report(old_contract: dict, new_contract: dict) -> dict:
    """Enhanced compatibility report with visualization data"""
    report = {
        "compatible": [],
        "breaking": [],
        "warnings": [],
        "diffs": [],
        "dependencies": [],
        "consumers": find_consumers(old_contract),
        "visualization": {
            "summary": "",
            "details": ""
        }
    }

    # Populate diffs and change categories
    for name, old_item in old_contract.items():
        new_item = new_contract.get(name)

        if not new_item:
            diff = {
                "id": f"removed_{name}",
                "name": name,
                "type": old_item.get("type", "function"),
                "change_type": "removed",
                "old_signature": old_item
            }
            report['diffs'].append(diff)
            report['breaking'].append(diff)
            continue

        # Generate detailed diff
        diff = generate_item_diff(old_item, new_item)
        if diff:
            report['diffs'].append(diff)
            if is_breaking_diff(diff):
                report['breaking'].append(diff)
            else:
                report['compatible'].append(diff)

    # Find new items
    for name, new_item in new_contract.items():
        if name not in old_contract:
            diff = {
                "id": f"added_{name}",
                "name": name,
                "type": new_item.get("type", "function"),
                "change_type": "added",
                "new_signature": new_item
            }
            report['diffs'].append(diff)
            report['warnings'].append(diff)

    # Build dependency graph
    report['dependencies'] = build_dependency_graph(report['diffs'])


    # ZVIC Error Visualization

    Error visualization in ZVIC is designed for clarity, actionability, and workflow integration. All reporting is visual, structural, and multi-level, with no code examples or imperative logic in the spec.

    ## Visualization Layers

    ### 1. Error Summary & Distribution

    #### Error Type Pie Chart
    ```mermaid
    pie showData
            title Error Distribution
            "Signature Mismatch" : 4
            "Kind Mismatch" : 2
            "Protocol Violation" : 1
            "Other" : 3
    ```

    #### Error Table

    | Error ID | Type                | Location         | Message                                 | Context/Notes         |
    |----------|---------------------|------------------|-----------------------------------------|-----------------------|
    | ZV5001   | Kind Mismatch       | foo/bar.py:12    | Container kind mismatch: expected *→*, actual * | Function 'foo'         |
    | ZV5002   | Protocol Violation  | api/schema.py:88 | Protocol 'Tensor' attribute 'dtype' mismatch | dtype: float32 vs int64 |
    | ZV5003   | Signature Mismatch  | util.py:44       | Parameter count changed                 | Added param 'flags'   |

    ### 2. Error Impact & Timeline

    #### Impact Graph
    ```mermaid
    graph TD
        E1[Kind Mismatch: foo]:::breaking
        E2[Protocol Violation: Tensor]:::warning
        E1 --> S1[ServiceA]
        E2 --> S2[ServiceB]
        classDef breaking fill:#ffcccc,stroke:#ff0000
        classDef warning fill:#ffffcc,stroke:#ffcc00
    ```

    #### Error Timeline
    ```mermaid
  <div class="card">
    <h2>Breaking Changes</h2>
    {render_html_diff_section(report['breaking'])}
  </div>


    ---

    ## Workflow Integration

    ### CLI & CI/CD

    | Command/Step | Description |
    |--------------|-------------|
    | `zvic check --errors contract.json` | Outputs error summary and details |
    | `zvic visualize --errors error_report.json --format html > errors.html` | Generates HTML dashboard |
    | `zvic monitor --dir ./src --format vscode` | Watches for errors and outputs VS Code diagnostics |

    #### Example CI/CD YAML
    ```yaml
    name: ZVIC Error Check
    on: [pull_request]
    jobs:
        error-check:
            runs-on: ubuntu-latest
            steps:
            - name: Checkout
                uses: actions/checkout@v3
            - name: Set up Python
                uses: actions/setup-python@v3
            - name: Install ZVIC
                run: pip install zvic
            - name: Generate contract
                run: zvic generate --module api -o contract.json
            - name: Check errors
                run: zvic check --errors contract.json --output error_report.json
            - name: Upload error report
                uses: actions/upload-artifact@v3
                with:
                    name: error-report
                    path: error_report.json
            - name: Fail on errors
                run: |
                    jq -e '.breaking | length == 0' error_report.json
    ```

    ---

    ## Key Benefits

    - **Actionable:** Clear visualization of error types, locations, and impact
    - **Multi-Format:** Console, HTML, VS Code, and Mermaid.js diagrams
    - **Historical:** Timeline and impact views
    - **Integrated:** CLI and CI/CD pipeline support

    This system transforms ZVIC error reports into actionable, visual insights for teams—no semantic versioning required.
  <div class="card">
    <h2>Warnings</h2>
    {render_html_diff_section(report['warnings'])}
  </div>

  <script>
    mermaid.initialize({{ startOnLoad: true }});
  </script>
</body>
</html>
"""
```

#### VS Code Extension Integration:

```python
def generate_vscode_diagnostics(report: dict) -> list:
    """Generate VS Code diagnostic markers"""
    diagnostics = []

    for item in report['diffs']:
        severity = 1 if item in report['breaking'] else 2  # Error vs Warning

        # Create diagnostic for each change
        for param_diff in item.get('param_diffs', []):
            diagnostic = {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 0}
                },
                "severity": severity,
                "message": f"Parameter change: {param_diff['changes']}",
                "source": "ZVIC",
                "relatedInformation": [
                    {
                        "location": {
                            "uri": "file:///contract.json",
                            "range": {"start": {"line": 0, "character": 0}}
                        },
                        "message": f"Original: {param_diff['old']}"
                    },
                    {
                        "location": {
                            "uri": "file:///new_contract.json",
                            "range": {"start": {"line": 0, "character": 0}}
                        },
                        "message": f"New: {param_diff['new']}"
                    }
                ]
            }
            diagnostics.append(diagnostic)

    return diagnostics
```

## Advanced Visualization Features

### 1. Change Timeline Visualization

```python
def render_change_timeline(contract_history: list) -> str:
    """Visualize contract evolution over time"""
    output = ["```mermaid\ntimeline"]

    for i, contract in enumerate(contract_history):
        changes = []
        if i > 0:
            prev = contract_history[i-1]
            diff = generate_compatibility_report(prev, contract)
            changes.append(f"Breaking: {len(diff['breaking'])}")
            changes.append(f"Changes: {len(diff['diffs'])}")

        date = contract['metadata'].get('timestamp', f"Version {i+1}")
        title = contract['metadata'].get('version', f"Contract {i+1}")
        output.append(f"    {date} : {title} : {', '.join(changes)}")

    output.append("```")
    return "\n".join(output)
```

### 2. Schema Evolution Tree

```python
def render_schema_evolution(schema_history: dict) -> str:
    """Show evolution of a specific schema"""
    output = ["```mermaid\ngraph LR"]

    versions = sorted(schema_history.keys())
    for i, version in enumerate(versions):
        schema = schema_history[version]

        # Node with schema summary
        node_label = (
            f"{version}\\n"
            f"Fields: {len(schema['fields']}\\n"
            f"Changes: {schema.get('change_count', 0)}"
        )
        output.append(f"  v{version}[{node_label}]")

        # Connection to previous version
        if i > 0:
            prev_version = versions[i-1]
            changes = schema.get('changes_from_previous', [])
            change_desc = "\\n".join(changes[:2])
            if len(changes) > 2:
                change_desc += "\\n..."
            output.append(f"  v{prev_version} -->|\"{change_desc}\"| v{version}")

    output.append("```")
    return "\n".join(output)
```

### 3. Compatibility Risk Heatmap

```python
def render_risk_heatmap(contract: dict) -> str:
    """Show risk distribution across contract"""
    output = ["```mermaid\nheatmap"]

    # Categorize items by risk level
    risk_categories = {
        "high": [],
        "medium": [],
        "low": []
    }

    for name, item in contract.items():
        risk = calculate_risk_score(item)
        risk_categories[risk].append(name)

    # Generate heatmap
    output.append("    title Contract Risk Distribution")
    output.append(f"    \"High Risk\" : {len(risk_categories['high'])}")
    output.append(f"    \"Medium Risk\" : {len(risk_categories['medium'])}")
    output.append(f"    \"Low Risk\" : {len(risk_categories['low'])}")

    output.append("```\n")

    # Detailed breakdown
    output.append("### High Risk Items")
    output.append("\n".join([f"- {name}" for name in risk_categories['high']]))

    return "\n".join(output)

def calculate_risk_score(item: dict) -> str:
    """Determine risk level for contract item"""
    if item.get('type') in ['rpc_endpoint', 'message_schema']:
        return "high"
    if item.get('consumers', 0) > 3:
        return "high"
    if item.get('type') == 'internal_function':
        return "low"
    return "medium"
```

## Integration with ZVIC Workflow

### CLI Interface

```bash
zvic diff --old contract_v1.json --new contract_v2.json
# Outputs console report

zvic visualize --report diff_report.json --format html > report.html
# Generates HTML dashboard

zvic monitor --dir ./src --format vscode
# Watches for changes and outputs VS Code diagnostics
```

### CI/CD Integration

```yaml
# .github/workflows/zvic.yml
name: ZVIC Contract Check
on: [pull_request]

jobs:
  contract-check:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3

    - name: Install ZVIC
      run: pip install zvic

    - name: Generate contracts
      run: |
        zvic generate --module api -o contract_old.json
        git checkout main
        zvic generate --module api -o contract_new.json
        git checkout $GITHUB_HEAD_REF

    - name: Check compatibility
      run: |
        zvic diff --old contract_old.json --new contract_new.json --output report.json

    - name: Upload report
      uses: actions/upload-artifact@v3
      with:
        name: contract-report
        path: report.json

    - name: Fail on breaking changes
      if: ${{ failure() }}
      run: |
        jq -e '.breaking | length == 0' report.json
```

## Key Benefits of This Approach

**Actionable Insights:**
- Clear visualization of breaking changes
- Parameter-level diff highlighting
- Impact analysis for dependency graphs

**Multi-Format Support:**
- Console output for CLI usage
- HTML dashboards for team sharing
- VS Code integration for developers
- Mermaid.js diagrams for documentation

**Historical Context:**
- Timeline visualization of contract evolution
- Schema version trees
- Change frequency heatmaps

**Integrated Workflow:**
- CI/CD pipeline integration
- Automated breaking change detection
- Pre-commit hooks for local development

This visualization system transforms ZVIC compatibility reports from technical artifacts into actionable insights, enabling teams to quickly understand and respond to interface changes without semantic versioning.