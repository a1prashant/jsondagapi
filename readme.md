# jsondagapi

`jsondagapi` is a **JSON-first, versioned API platform** for defining, validating, analyzing, and executing **DAG-based workflows** using **LangGraph** as the execution backend.

The primary goal of this project is to provide a **stable, standardized, and extensible API layer** that can be safely consumed by **multiple internal teams**, while insulating them from execution-engine and LangGraph version churn.

---

## 1. Why jsondagapi Exists

Most workflow orchestration systems tightly couple:

* workflow definition
* execution semantics
* runtime engine

`jsondagapi` intentionally separates these concerns.

### jsondagapi provides:

* A **canonical JSON contract** for DAG workflows
* Strong **validation and analysis APIs**
* A **versioned REST API** suitable for multi-team usage
* A clean **adapter layer** over LangGraph (supporting multiple versions)

### jsondagapi does NOT try to be:

* A general-purpose scheduler
* A BPM or UI-driven workflow system
* A replacement for mature orchestration engines

It is an **API façade and control plane**, not a monolithic orchestrator.

---

## 2. Core Capabilities

### Workflow Lifecycle

* Create workflow definitions
* Update and fetch workflows
* Validate workflow structure and DAG correctness
* Analyze workflow topology (depth, fan-out, etc.)

### Execution

* Execute workflows as immutable runtime instances
* Track workflow- and node-level execution state
* Retrieve execution status and runtime metadata

### Safety & Correctness

* Strict DAG guarantees (no cycles)
* Deterministic execution order
* Strong request/response validation
* Explicit error contracts

---

## 3. High-Level Architecture

```
Client Applications
        │
        ▼
FastAPI API Layer (versioned)
        │
        ▼
Application / Use-Case Layer
        │
        ▼
Domain Layer (DAG model & rules)
        │
        ▼
Execution Engine
        │
        ▼
LangGraph Adapter (versioned)
        │
        ▼
LangGraph Runtime
```

### Architectural Principles

* **API-first** and **contract-driven**
* **Domain-centric design**
* **Adapter pattern** for external dependencies
* Clear separation of responsibilities

---

## 4. Versioning Strategy

`jsondagapi` uses **explicit URL-based versioning** with two independent axes:

```
/api/v1/langgraph/0.3/...
```

* `v1` → API contract version (client-facing)
* `langgraph/0.3` → execution backend capability

This allows:

* parallel support for multiple LangGraph versions
* backward-compatible API evolution
* safe backend upgrades

---

## 5. API Design Overview

### Primary Resources

1. **Workflow** – static DAG definition
2. **Execution** – runtime instance of a workflow
3. **Validation / Analysis** – read-only operations

### Endpoint Groups (Conceptual)

#### Workflow APIs

```
POST   /workflows
PUT    /workflows/{workflow_id}
GET    /workflows/{workflow_id}
GET    /workflows
DELETE /workflows/{workflow_id}   (optional)
```

#### Validation & Analysis APIs

```
POST /workflows/validate
POST /workflows/analyze
```

#### Execution APIs

```
POST /executions
GET  /executions/{execution_id}
GET  /executions/{execution_id}/status
GET  /executions/{execution_id}/nodes
POST /executions/{execution_id}/cancel   (optional)
```

---

## 6. API Conventions

### Request Conventions

* JSON only
* Explicit required fields
* Deterministic validation failures

### Response Envelope

All API responses follow a consistent structure:

```json
{
  "data": {},
  "meta": {
    "request_id": "uuid",
    "api_version": "v1"
  },
  "errors": []
}
```

---

## 7. Error Handling Model

### Error Categories

| Category        | HTTP Code | Description               |
| --------------- | --------- | ------------------------- |
| ValidationError | 400       | Invalid input or DAG      |
| NotFound        | 404       | Resource not found        |
| Conflict        | 409       | Resource conflict         |
| ExecutionError  | 422       | Runtime execution failure |
| SystemError     | 500       | Unexpected internal error |

### Error Payload Example

```json
{
  "error": {
    "code": "DAG_CYCLE_DETECTED",
    "message": "Workflow contains a cycle",
    "details": {
      "nodes": ["A", "B", "C"]
    }
  }
}
```

---

## 8. Folder Structure (Agreed)

```
jsondagapi/
├── main.py
├── settings.py
│
├── api_v1/
│   ├── routes.py        # All v1 routes
│   ├── schemas.py       # Request/response DTOs
│   ├── dependencies.py
│   └── __init__.py
│
├── application/         # Use-case orchestration
├── domain/              # DAG model, rules, state machine
├── engine/              # Execution engine
├── adapters/            # LangGraph adapters (versioned)
├── validation/          # Schema & structural validation
├── observability/       # Logging & tracing hooks
└── tests/               # POC-level tests
```

This structure is intentionally **flat yet modular**, optimized for clarity and evolution.

---

## 9. Design Principles

* **SOLID** – clear responsibilities and extensibility
* **DRY** – no duplicated logic across layers
* **KISS** – avoid premature abstraction
* **Explicit over implicit** – predictable behavior

---

## 10. Non-Goals (Current Scope)

The following are explicitly out of scope for the initial POC:

* Persistence layer
* Distributed scheduling
* Message queues / workers
* Authentication & authorization
* UI / dashboards

The architecture is designed so these can be added later **without breaking API contracts**.

---

## 11. Current Status

✅ API layer design finalized
✅ Versioning strategy locked
✅ Folder structure agreed

### Next Planned Steps

1. Domain model & workflow state machine
2. Canonical DAG JSON schema
3. Execution semantics
4. LangGraph adapter implementation

---

## 12. Audience

This repository is intended for:

* Platform and backend engineers
* Teams integrating workflow capabilities via APIs
* Architects reviewing workflow and orchestration patterns

---

## 13. License & Usage

Internal platform component (license and usage to be defined).
# jsondagapi
