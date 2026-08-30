# Pattern: Recursive Flow Parsing

## Description

Parse nested automation-style structures recursively, adding structural nodes where needed and retaining each relationship's configuration location and certainty.

## When to Use

Use when supporting an additional control structure, trigger, condition, action, or target shape in a flow configuration.

## Pattern

Route all relationships through `FlowParser.edge()`, use `_struct()` for visible control-flow nodes, recurse into nested sequences, and preserve template-derived references as dynamic rather than evaluating them.

## Example

```python
if "if" in action:
    branch = self._struct(owner, "branch", "If", loc)
    conditions = self.condition(branch, action["if"], loc + ".if")
    condition_owner = conditions[-1] if conditions else branch
    self.actions(condition_owner, action.get("then", []), loc + ".then")
    self.actions(condition_owner, action.get("else", []), loc + ".else")
```

## Files Using This Pattern

- `custom_components/ha_flow_map/parsers/automation.py` — recursively parses triggers, conditions, branches, waits, repeats, services, and targets.
- `custom_components/ha_flow_map/parsers/template.py` — extracts literal references and identifies dynamic values without rendering templates.
- `tests/test_parsers.py` — verifies nested flow behavior and dynamic-reference marking.

## Related

- [Decision: Graph-Based Relationship Model](../../decisions/002-graph-based-relationship-model.md)
- [Decision: Safe and Bounded Data Exposure](../../decisions/004-safe-and-bounded-data-exposure.md)
- [Feature: Relationship Discovery](../../intent/feature-relationship-discovery.md)

## Status

- **Created**: 2026-08-30
- **Status**: Active
