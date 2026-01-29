# LangGraph Adapter Mapping  
**jsondagapi ↔ LangGraph Runtime**

## 1. Purpose of This Document

This document defines a **strict, deterministic mapping** between:

- **jsondagapi Canonical Workflow JSON (v1)**  
and  
- **LangGraph runtime constructs**

It exists to ensure:
- No feature drift
- Predictable execution
- Adapter replaceability
- Clear ownership boundaries

> ⚠️ This is **not** an exposure of LangGraph internals.  
> It is a *controlled translation layer*.

---

## 2. Adapter Responsibilities (Non-Negotiable)

The LangGraph adapter **MUST**:

1. Accept only **validated canonical workflows**
2. Never mutate workflow structure at runtime
3. Enforce DAG invariants even if LangGraph allows otherwise
4. Treat LangGraph as an **execution engine**, not a source of truth
5. Surface runtime state & errors back to jsondagapi verbatim

---

## 3. High-Level Mapping Overview

| jsondagapi Concept | LangGraph Equivalent |
|-------------------|----------------------|
| Workflow | `StateGraph` |
| Node | `add_node()` |
| Edge | `add_edge()` |
| Conditional Edge | `add_conditional_edges()` |
| Execution State | Graph State |
| Task Node | Runnable / Tool |
| Decision Node | Router function |
| Subgraph Node | Nested `StateGraph` |
| Execution Run | `graph.invoke()` |
| Errors | Exceptions / Failures |

---

## 4. Workflow Mapping

### jsondagapi
```json
{
  "workflow_id": "order_processing",
  "version": "1.0.0",
  "entry_node": "validate_order"
}
````

### LangGraph

```python
graph = StateGraph(state_schema)
graph.set_entry_point("validate_order")
```

**Rules**

* `workflow_id` → metadata only
* `version` → metadata only
* `entry_node` → `set_entry_point()`

---

## 5. Node Mapping

### 5.1 Task Node

#### jsondagapi

```json
{
  "id": "charge_payment",
  "type": "task",
  "executor": {
    "mode": "callback",
    "callback_id": "payment-service"
  }
}
```

#### LangGraph

```python
async def charge_payment(state):
    return await callback_executor("payment-service", state)

graph.add_node("charge_payment", charge_payment)
```

**Adapter Rules**

* No inline Python logic from workflow JSON
* Executor resolved via adapter registry
* State passed immutably (copy-on-write)

---

### 5.2 Decision Node (Expression-Based)

#### jsondagapi

```json
{
  "id": "payment_decision",
  "type": "decision",
  "decision_type": "expression",
  "expression": {
    "operator": "==",
    "left": "$.payment.status",
    "right": "success"
  }
}
```

#### LangGraph

```python
def payment_decision(state):
    return evaluate_expression(expression, state)
```

```python
graph.add_conditional_edges(
    "payment_decision",
    payment_decision,
    {
        "true": "ship_order",
        "false": "cancel_order"
    }
)
```

**Adapter Rules**

* Expression language evaluated **outside** LangGraph logic
* Only outcome labels returned

---

### 5.3 Decision Node (Callback-Based)

#### jsondagapi

```json
{
  "id": "fraud_check",
  "type": "decision",
  "decision_type": "callback",
  "callback_id": "fraud-engine"
}
```

#### LangGraph

```python
async def fraud_check(state):
    return await callback_executor("fraud-engine", state)
```

**Adapter Rules**

* Adapter must block or await callback
* Callback must return a valid outcome label

---

## 6. Edge Mapping

### jsondagapi

```json
{
  "from": "payment_decision",
  "to": "ship_order",
  "condition": "success"
}
```

### LangGraph

```python
graph.add_conditional_edges(
    "payment_decision",
    router,
    {"success": "ship_order"}
)
```

**Invariants**

* Exactly one outgoing edge per outcome
* Unmatched outcomes → execution error

---

## 7. Subgraph Mapping

### jsondagapi

```json
{
  "id": "shipping_flow",
  "type": "subgraph",
  "subgraph_ref": {
    "workflow_id": "shipping",
    "version": "2.1.0"
  }
}
```

### LangGraph

```python
subgraph = build_graph(sub_workflow)
graph.add_node("shipping_flow", subgraph)
```

**Rules**

* Subgraph must be built first
* State contract must be compatible
* No cyclic subgraph references

---

## 8. State Mapping

### jsondagapi

```json
"state_schema": {
  "order_id": "string",
  "payment": "object",
  "status": "string"
}
```

### LangGraph

```python
class State(TypedDict):
    order_id: str
    payment: dict
    status: str
```

**Rules**

* Adapter generates TypedDict or equivalent
* No dynamic state keys allowed at runtime
* State mutations validated post-node execution

---

## 9. Execution Mapping

### jsondagapi

```http
POST /executions
```

### LangGraph

```python
result = await graph.invoke(initial_state)
```

**Adapter Responsibilities**

* Map execution_id
* Track node-by-node status
* Emit lifecycle events

---

## 10. Error Mapping

| jsondagapi Error | LangGraph Source     |
| ---------------- | -------------------- |
| VALIDATION_ERROR | Pre-build checks     |
| EXECUTION_ERROR  | Node exception       |
| TIMEOUT          | Async timeout        |
| CALLBACK_FAILED  | External service     |
| INVALID_OUTCOME  | Conditional mismatch |

**Rule**

> No raw LangGraph exceptions escape the adapter.

---

## 11. Explicit Non-Goals (Frozen)

The adapter **WILL NOT**:

* Execute arbitrary Python from workflow JSON
* Allow runtime graph mutation
* Support cyclic graphs
* Support streaming tokens (v1)
* Expose LangGraph internals

---

## 12. Adapter Extensibility Contract

Future engines (Temporal, Ray, custom) must:

* Implement the same adapter interface
* Respect canonical schema invariants
* Emit identical execution events

This ensures **engine portability without API change**.

---

## 13. Final Architectural Guarantee

> If a workflow is valid in `jsondagapi`,
> it **must execute identically** on any compliant adapter.

That is the platform promise.

