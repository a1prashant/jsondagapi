# Conditions & Execution Model — jsondagapi

This document formalizes how **conditions**, **decisions**, and **execution** are handled in `jsondagapi`. It is a foundational architectural contract intended for multi-team usage and long-term extensibility.

---

## 1. Core Architectural Invariant

**jsondagapi is an orchestration engine, not a business logic engine.**

The engine:

* Manages workflow structure (DAG)
* Maintains execution state
* Orchestrates node execution
* Evaluates routing outcomes

The engine **never executes arbitrary business code**.

---

## 2. Separation of Concerns

Three concerns are intentionally separated:

| Concern                         | Responsibility                   |
| ------------------------------- | -------------------------------- |
| Workflow structure              | jsondagapi                       |
| Condition / decision evaluation | Condition evaluators (pluggable) |
| Task execution                  | External executors / services    |

This separation ensures security, scalability, and multi-language support.

---

## 3. Workflow State Model

* Each workflow execution maintains a **mutable execution state**
* State consists of key–value pairs
* Values may be of any JSON-serializable datatype

### State Access Rules

| Actor          | Access       |
| -------------- | ------------ |
| Task nodes     | Read + Write |
| Decision nodes | Read-only    |
| Conditions     | Read-only    |

State mutation outside task nodes is forbidden.

---

## 4. Condition Types (Routing Logic)

jsondagapi supports **two and only two** condition mechanisms in v1.

### 4.1 Expression-Based Conditions

**Purpose:** Fast, deterministic routing based on workflow state

**Characteristics:**

* Declarative
* Side-effect free
* Synchronous
* Deterministic

**Example:**

```json
{
  "condition": {
    "type": "expression",
    "language": "jsonlogic",
    "expression": {
      ">": [
        { "var": "score" },
        0.8
      ]
    }
  }
}
```

The engine delegates evaluation to a pluggable evaluator based on `language`.

---

### 4.2 Callback-Based Conditions (External Decisions)

**Purpose:** Externalized decisions that cannot be expressed as pure expressions

Typical use cases:

* ML inference
* Human-in-the-loop approval
* External policy engines
* Compliance or regulatory checks

> Callback conditions represent **decisions**, not tasks.

---

## 5. Decision Nodes (Recommended Pattern)

Rather than embedding callbacks in edges, jsondagapi strongly recommends **explicit decision nodes**.

### 5.1 Decision Node Definition

```json
{
  "id": "decision_1",
  "type": "decision",
  "executor": {
    "type": "callback",
    "config": {
      "timeout_seconds": 60
    }
  }
}
```

### Decision Node Rules

* Read-only access to workflow state
* Produces **routing outcome**, not data
* Does not mutate execution state

---

## 6. Callback Decision Flow

### 6.1 Engine → External System (Decision Request)

```json
{
  "execution_id": "exec_123",
  "node_id": "decision_1",
  "state": {
    "score": 0.82,
    "user_type": "new"
  },
  "possible_outcomes": ["approve", "reject", "manual_review"]
}
```

---

### 6.2 External System → Engine (Decision Response)

```json
{
  "outcome": "approve"
}
```

The engine maps `outcome` to outgoing edges.

---

## 7. Edge Routing Semantics

Edges following a decision node are labeled implicitly or explicitly via metadata.

```json
{
  "from": "decision_1",
  "to": "node_approve",
  "metadata": {
    "outcome": "approve"
  }
}
```

Only edges matching the selected outcome are activated.

---

## 8. Failure Semantics

Deterministic failure handling is mandatory.

| Scenario                 | Engine Behavior    |
| ------------------------ | ------------------ |
| Callback timeout         | Fail decision node |
| Invalid callback payload | Fail execution     |
| Unknown outcome          | Fail execution     |
| Retry exhausted          | Fail execution     |

No implicit fallbacks are allowed.

---

## 9. Task Execution Model (Recap)

Task nodes execute business logic via **external executors**.

Supported execution styles:

* Synchronous HTTP (POC / limited use)
* Asynchronous callback (recommended)
* Event-driven (future)

Task nodes may:

* Mutate state
* Emit outputs
* Trigger retries

---


## 10. Summary of Guarantees

jsondagapi guarantees:

* No embedded business logic execution
* Deterministic routing
* Clear separation between decision and execution
* Multi-team safe extensibility

This model aligns with proven workflow engines while remaining LangGraph-compatible and future-proof.

---

## 11. Condition & Decision Catalog (v1)

This section defines the **allowed keys, values, operators, and contracts** for conditions and decision execution. This catalog is intentionally explicit to ensure consistency across teams.

---

## 11.1 Condition Object – Common Keys

Applicable to all condition types.

| Key        | Type   | Required | Description                                |
| ---------- | ------ | -------- | ------------------------------------------ |
| `type`     | string | Yes      | `expression` or `callback`                 |
| `version`  | string | No       | Condition contract version (default: `v1`) |
| `metadata` | object | No       | Non-functional annotations                 |

---

## 11.2 Expression-Based Condition Catalog

### Required Keys

| Key          | Type   | Description                      |
| ------------ | ------ | -------------------------------- |
| `language`   | string | Expression language identifier   |
| `expression` | object | Declarative condition expression |

### Supported Expression Languages (v1)

| Language    | Description                                   |
| ----------- | --------------------------------------------- |
| `jsonlogic` | JSON Logic standard                           |
| `cel`       | Common Expression Language (read-only subset) |

---

### Supported Operators (JSONLogic – v1 Subset)

#### Comparison Operators

| Operator | Meaning               |
| -------- | --------------------- |
| `==`     | Equal                 |
| `!=`     | Not equal             |
| `>`      | Greater than          |
| `<`      | Less than             |
| `>=`     | Greater than or equal |
| `<=`     | Less than or equal    |

#### Logical Operators

| Operator | Meaning     |
| -------- | ----------- |
| `and`    | Logical AND |
| `or`     | Logical OR  |
| `!`      | Logical NOT |

#### State Access

| Operator | Meaning                         |
| -------- | ------------------------------- |
| `var`    | Read value from execution state |

> Only **read-only access** to state is permitted.

---

## 11.3 Callback-Based Condition Catalog

Callback conditions represent **external decision evaluation**.

### Required Keys

| Key            | Type   | Description                         |
| -------------- | ------ | ----------------------------------- |
| `type`         | string | Must be `callback`                  |
| `decision_key` | string | Logical identifier for the decision |
| `callback`     | object | Callback execution configuration    |

### Callback Configuration Keys

| Key               | Type    | Description           |
| ----------------- | ------- | --------------------- |
| `mode`            | string  | `async` (default)     |
| `timeout_seconds` | integer | Max wait time         |
| `retry_policy`    | object  | Optional retry config |

---

## 11.4 Decision Node Executor Catalog

Decision nodes must use **callback executors only**.

### Executor Object Keys

| Key       | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `type`    | string | Yes      | Must be `callback`     |
| `version` | string | No       | Executor version       |
| `config`  | object | Yes      | Executor configuration |

### Executor Config Keys

| Key               | Type    | Description      |
| ----------------- | ------- | ---------------- |
| `timeout_seconds` | integer | Decision timeout |
| `retry_policy`    | object  | Retry behavior   |

---

## 11.5 Decision Callback Payload Catalog

### Engine → External System

| Field               | Type          | Description              |
| ------------------- | ------------- | ------------------------ |
| `execution_id`      | string        | Execution identifier     |
| `node_id`           | string        | Decision node ID         |
| `state`             | object        | Read-only workflow state |
| `possible_outcomes` | array[string] | Allowed outcomes         |

### External System → Engine

| Field      | Type   | Description          |
| ---------- | ------ | -------------------- |
| `outcome`  | string | Selected outcome     |
| `metadata` | object | Optional annotations |

---

## 11.6 Edge Outcome Mapping Catalog

Edges originating from decision nodes map outcomes explicitly.

| Edge Metadata Key | Description                           |
| ----------------- | ------------------------------------- |
| `outcome`         | Outcome value that activates the edge |

Unknown or missing outcomes result in execution failure.

---

## 11.7 Failure Codes (Recommended)

| Code                         | Meaning                        |
| ---------------------------- | ------------------------------ |
| `DECISION_TIMEOUT`           | Callback timeout               |
| `INVALID_DECISION_RESPONSE`  | Malformed callback payload     |
| `UNKNOWN_OUTCOME`            | Outcome not mapped to any edge |
| `CONDITION_EVALUATION_ERROR` | Expression evaluation failure  |

---

## 12. Stability & Extension Rules

* New operators must be **additive**
* Existing operators must not change semantics
* New condition languages require explicit versioning
* Callback contracts are backward compatible within major versions

---

## 13. Node Taxonomy (v1 – Frozen)

This section defines the **canonical node types** supported by `jsondagapi` v1. Node taxonomy is a critical invariant: APIs, validation rules, execution semantics, and callbacks all depend on it.

---

## 13.1 Supported Node Types

| Node Type  | Purpose             | Executes Business Logic | Mutates State          |
| ---------- | ------------------- | ----------------------- | ---------------------- |
| `task`     | Perform work        | Yes (external)          | Yes                    |
| `decision` | Decide routing      | No                      | No                     |
| `subgraph` | Reusable DAG        | Indirect                | Depends on inner nodes |
| `tool`     | External capability | Yes (external)          | Yes                    |

No other node types are permitted in v1.

---

## 13.2 Common Node Schema (All Types)

All nodes share the following base structure:

```json
{
  "id": "string",
  "type": "task | decision | subgraph | tool",
  "name": "string",
  "description": "string",
  "metadata": {}
}
```

---

## 13.3 Task Nodes

### Purpose

Execute business logic via external systems.

### Characteristics

* Side effects allowed
* State mutation allowed
* Supports retries and timeouts

### Required Keys

| Key        | Type   | Required |
| ---------- | ------ | -------- |
| `executor` | object | Yes      |

### Allowed Executors (v1)

| Executor Type | Description                              |
| ------------- | ---------------------------------------- |
| `http`        | Synchronous HTTP call (limited use)      |
| `callback`    | Async execution with completion callback |
| `event`       | Event-driven execution (optional)        |

### State Mutation Rule

Task nodes may:

* Add new state keys
* Update existing keys

They must not:

* Delete state keys implicitly

---

## 13.4 Decision Nodes

### Purpose

Determine routing between nodes.

### Characteristics

* No business logic execution
* Read-only access to state
* Produces routing outcome only

### Required Keys

| Key        | Type   | Required |
| ---------- | ------ | -------- |
| `executor` | object | Yes      |

### Allowed Executors

| Executor Type | Allowed |
| ------------- | ------- |
| `callback`    | Yes     |
| `http`        | No      |
| `event`       | No      |

### State Rule

Decision nodes must not mutate state.

---

## 13.5 Subgraph Nodes

### Purpose

Encapsulate reusable workflows.

### Characteristics

* References another workflow definition
* Execution delegated to inner DAG

### Required Keys

| Key            | Type   | Required |
| -------------- | ------ | -------- |
| `subgraph_ref` | string | Yes      |

### State Handling

* Inherits parent state
* Inner state changes are merged back

---

## 13.6 Tool Nodes

### Purpose

Invoke standardized external capabilities (LLMs, tools, agents).

### Characteristics

* Specialized form of task node
* Often used in LangGraph contexts

### Allowed Executors

| Executor Type | Description |
| ------------- | ----------- |
| `callback`    | Default     |
| `event`       | Optional    |

State mutation rules are identical to task nodes.

---

## 13.7 Retry & Timeout Semantics

| Node Type  | Retry Allowed | Timeout Allowed |
| ---------- | ------------- | --------------- |
| `task`     | Yes           | Yes             |
| `decision` | Limited       | Yes             |
| `subgraph` | Inherited     | Inherited       |
| `tool`     | Yes           | Yes             |

Retries on decision nodes apply only to callback failures.

---

## 13.8 Validation Rules (Mandatory)

The engine must enforce:

* No outgoing edges from terminal nodes
* Decision nodes must have ≥1 outgoing edge
* Only decision nodes may produce routing outcomes
* DAG must remain acyclic after any update

---

## 13.9 Extension Rules

* New node types require a major version bump
* Executor additions are backward-compatible
* Node semantics must remain stable within v1

---

**Status:** Node taxonomy is frozen for v1 and must not be altered without a breaking-version release.


## 14. Canonical Workflow JSON Schema (v1 – Frozen)

This section defines the **canonical workflow JSON contract** for `jsondagapi`. This schema is the authoritative representation of a workflow and underpins all APIs, validation rules, and execution behavior.

---

## 14.1 Top-Level Workflow Object

### Required Fields

| Field         | Type   | Description                         |
| ------------- | ------ | ----------------------------------- |
| `workflow_id` | string | Globally unique workflow identifier |
| `name`        | string | Human-readable name                 |
| `version`     | string | Workflow version (semantic)         |
| `nodes`       | array  | List of node definitions            |
| `edges`       | array  | List of directed edges              |

### Optional Fields

| Field         | Type   | Description                    |
| ------------- | ------ | ------------------------------ |
| `description` | string | Workflow description           |
| `metadata`    | object | Arbitrary annotations          |
| `policies`    | object | Default retry/timeout policies |
| `inputs`      | object | Declared workflow inputs       |
| `outputs`     | object | Declared workflow outputs      |

---

## 14.2 Node Schema (v1)

```json
{
  "id": "string",
  "type": "task | decision | subgraph | tool",
  "name": "string",
  "description": "string",
  "executor": {},
  "retry_policy": {},
  "timeout_policy": {},
  "subgraph_ref": "string",
  "metadata": {}
}
```

### Required vs Optional (by node type)

| Field            | Task | Decision | Subgraph | Tool |
| ---------------- | ---- | -------- | -------- | ---- |
| `id`             | ✓    | ✓        | ✓        | ✓    |
| `type`           | ✓    | ✓        | ✓        | ✓    |
| `executor`       | ✓    | ✓        | ✗        | ✓    |
| `subgraph_ref`   | ✗    | ✗        | ✓        | ✗    |
| `retry_policy`   | ✓    | △        | △        | ✓    |
| `timeout_policy` | ✓    | ✓        | △        | ✓    |

△ = inherited or limited

---

## 14.3 Edge Schema (v1)

```json
{
  "from": "string",
  "to": "string",
  "condition": {},
  "metadata": {}
}
```

### Edge Rules

* `from` and `to` must reference existing node IDs
* Self-loops are forbidden
* Conditional edges are allowed only from `decision` nodes
* Default (unconditional) edges are allowed from task/subgraph/tool nodes

---

## 14.4 Workflow Invariants (Mandatory)

The engine must enforce the following invariants:

### DAG Constraints

* Workflow graph must be acyclic
* At least one start node must exist (node with no incoming edges)
* Terminal nodes must have no outgoing edges

### Node Constraints

* Node IDs must be unique within a workflow
* Node IDs are immutable after creation
* All nodes must be reachable from a start node

### Edge Constraints

* Decision nodes must have ≥1 outgoing edge
* Conditional edges must resolve to exactly one active path per execution

---

## 14.5 Versioning Strategy

### Workflow Versioning

* `version` follows semantic versioning: `MAJOR.MINOR.PATCH`
* Any structural change increments at least MINOR
* Breaking changes require MAJOR bump

### API vs Workflow Versioning

* Workflow version is independent of API version
* Same API version may manage multiple workflow versions

---

## 14.6 Partial Update Constraints

Partial updates are **intent-based**, not raw JSON patch.

### Allowed Partial Operations

| Operation          | Scope                                        |
| ------------------ | -------------------------------------------- |
| Add node           | `nodes`                                      |
| Update node config | `nodes/{id}`                                 |
| Remove node        | `nodes/{id}` (only if no edges reference it) |
| Add edge           | `edges`                                      |
| Remove edge        | `edges/{from}->{to}`                         |

### Forbidden Operations

* Changing `workflow_id`
* Changing node `id`
* Introducing cycles
* Updating execution-state-related fields

---

## 14.7 Full Example Workflow (v1)

```json
{
  "workflow_id": "user_onboarding",
  "name": "User Onboarding Flow",
  "version": "1.0.0",
  "description": "Validates and approves new users",
  "metadata": {
    "owner": "platform-team"
  },
  "nodes": [
    {
      "id": "validate_input",
      "type": "task",
      "name": "Validate Input",
      "executor": {
        "type": "callback"
      }
    },
    {
      "id": "risk_decision",
      "type": "decision",
      "name": "Risk Check",
      "executor": {
        "type": "callback",
        "config": { "timeout_seconds": 60 }
      }
    },
    {
      "id": "approve_user",
      "type": "task",
      "name": "Approve User",
      "executor": { "type": "callback" }
    },
    {
      "id": "reject_user",
      "type": "task",
      "name": "Reject User",
      "executor": { "type": "callback" }
    }
  ],
  "edges": [
    { "from": "validate_input", "to": "risk_decision" },
    {
      "from": "risk_decision",
      "to": "approve_user",
      "metadata": { "outcome": "approve" }
    },
    {
      "from": "risk_decision",
      "to": "reject_user",
      "metadata": { "outcome": "reject" }
    }
  ]
}
```

---

**Status:** Canonical workflow JSON schema is frozen for v1 and serves as the contract for all jsondagapi implementations.
