# jsondagapi – API Layer Documentation (v1)

This document defines the **external API contract** for `jsondagapi`. It is intended for application teams, platform integrators, and SDK developers. All APIs are versioned and align strictly with the **frozen canonical workflow schema (v1)**.

---

## 1. API Design Principles

* RESTful, resource-oriented APIs
* Versioned by **LangGraph compatibility** (`v1` initially)
* JSON-only request/response
* Explicit error handling
* **No execution of user-provided code**
* Deterministic behavior
* **Callbacks are explicit, pre-registered, and reference-only**
* No runtime overrides or implicit discovery

Base path:

```

/api/v1

````

---

## 2. Core Resources

| Resource      | Description                                      |
|---------------|--------------------------------------------------|
| `workflows`   | Workflow definitions (DAG structure)              |
| `executions`  | Runtime workflow executions                      |
| `nodes`       | Partial workflow operations                      |
| `edges`       | Partial workflow operations                      |
| `analysis`    | Validation & inspection                          |
| `callbacks`   | Registered external callback endpoints (static)  |

---

## 3. Workflow Definition APIs (CRUD)

### 3.1 Create Workflow

**POST** `/workflows`

#### Request

```json
{ <canonical workflow JSON v1> }
````

#### Response – 201

```json
{
  "workflow_id": "string",
  "version": "1.0.0",
  "status": "CREATED"
}
```

---

### 3.2 Get Workflow

**GET** `/workflows/{workflow_id}`

Query params:

* `version` (optional, default: latest)

#### Response – 200

```json
{ <canonical workflow JSON v1> }
```

---

### 3.3 Update Workflow (Full Replace)

**PUT** `/workflows/{workflow_id}`

#### Request

```json
{ <canonical workflow JSON v1> }
```

#### Response – 200

```json
{
  "workflow_id": "string",
  "version": "1.1.0",
  "status": "UPDATED"
}
```

---

### 3.4 Delete Workflow

**DELETE** `/workflows/{workflow_id}`

#### Response – 204

---

## 4. Partial Workflow Modification APIs

### 4.1 Add Node

**POST** `/workflows/{workflow_id}/nodes`

```json
{ <node schema> }
```

---

### 4.2 Update Node

**PUT** `/workflows/{workflow_id}/nodes/{node_id}`

```json
{ <node schema> }
```

---

### 4.3 Remove Node

**DELETE** `/workflows/{workflow_id}/nodes/{node_id}`

> Fails if edges reference this node.

---

### 4.4 Add Edge

**POST** `/workflows/{workflow_id}/edges`

```json
{ <edge schema> }
```

---

### 4.5 Remove Edge

**DELETE** `/workflows/{workflow_id}/edges`

Query params:

* `from`
* `to`

---

## 5. Validation & Analysis APIs

### 5.1 Validate Workflow

**POST** `/analysis/validate`

```json
{ <canonical workflow JSON v1> }
```

#### Response

```json
{
  "valid": true,
  "errors": []
}
```

---

### 5.2 Analyze Workflow

**POST** `/analysis/inspect`

```json
{ <canonical workflow JSON v1> }
```

#### Response

```json
{
  "node_count": 5,
  "edge_count": 4,
  "depth": 3,
  "decision_nodes": ["risk_decision"]
}
```

---

## 6. Execution APIs

### 6.1 Start Execution

**POST** `/executions`

```json
{
  "workflow_id": "string",
  "workflow_version": "1.0.0",
  "inputs": {}
}
```

#### Response – 201

```json
{
  "execution_id": "exec_123",
  "status": "CREATED"
}
```

---

### 6.2 Get Execution Status

**GET** `/executions/{execution_id}`

```json
{
  "execution_id": "exec_123",
  "workflow_id": "string",
  "status": "RUNNING",
  "current_node": "validate_input"
}
```

---

### 6.3 Cancel Execution

**POST** `/executions/{execution_id}/cancel`

---

## 7. Callback Registration APIs (Mandatory)

### 7.1 Register Callback Endpoints

Clients **must register callbacks before workflows reference them**.
There is **no runtime override, no discovery, and no implicit URL resolution**.

**POST** `/callbacks/register`

```json
{
  "service_name": "order-service",
  "environment": "prod",
  "base_url": "https://orders.mycorp.com",
  "callbacks": {
    "start-task":   { "path": "/callbacks/start" },
    "approve-task": { "path": "/callbacks/approve" },
    "reject-task":  { "path": "/callbacks/reject" }
  }
}
```

#### Response – 201

```json
{
  "service_name": "order-service",
  "environment": "prod",
  "registered_callbacks": ["start-task", "approve-task", "reject-task"]
}
```

---

### 7.2 List Registered Callbacks

**GET** `/callbacks`

```json
[
  {
    "callback_id": "approve-task",
    "service_name": "order-service",
    "environment": "prod",
    "url": "https://orders.mycorp.com/callbacks/approve",
    "status": "ACTIVE"
  }
]
```

---

### 7.3 Deregister Callback

**DELETE** `/callbacks/{callback_id}`

> Fails if referenced by an active workflow.

---

## 8. Execution Callback APIs (Inbound to jsondagapi)

These endpoints are invoked **by registered external services** to
update workflow state.

### 8.1 Task Completion Callback

**POST** `/executions/{execution_id}/nodes/{node_id}/complete`

```json
{
  "status": "COMPLETED",
  "outputs": {},
  "error": null
}
```

---

### 8.2 Decision Callback

**POST** `/executions/{execution_id}/decisions/{node_id}`

```json
{
  "outcome": "approve"
}
```

---

## 9. Callback Resolution Rules (Frozen)

* Workflows reference callbacks **only by `callback_id`**
* Callback URLs are resolved **exclusively from the registry**
* Callback IDs must exist at workflow creation time
* No execution-time overrides
* No per-execution base URLs
* Deterministic routing guaranteed

---

## 10. Error Model (Standard)

```json
{
  "error_code": "string",
  "message": "string",
  "details": {}
}
```

### Common Error Codes

| Code               | Meaning                    |
| ------------------ | -------------------------- |
| `INVALID_WORKFLOW` | Schema or DAG violation    |
| `NOT_FOUND`        | Resource missing           |
| `CONFLICT`         | Version or state conflict  |
| `EXECUTION_FAILED` | Runtime failure            |
| `UNKNOWN_CALLBACK` | Callback ID not registered |

---

## 11. Versioning Rules

* API version: path-based (`/api/v1`)
* Workflow version: semantic
* Callback contracts stable within API major version

---

## 12. Contract Stability

This API document is **normative**.

Implementations must not deviate from:

* Canonical workflow schema
* Node taxonomy
* Callback registration model
* Execution semantics

Breaking changes require a new API major version.

---

**Status:** API layer frozen for v1 pending implementation feedback.

