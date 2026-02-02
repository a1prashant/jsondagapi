Design `guardrail-apis` for a Multi-Agent System

> You are a senior platform architect designing a **guardrail server** for a **multi-agent AI system**.
>
> The system must be called **`guardrail-apis`** and must follow these constraints **strictly**:
>
> ### Core Constraints
>
> * Architecture must be **flat** (no layered folders, no deep nesting)
> * Focus on **deterministic, classic, production-grade guardrails**
> * Suitable for **multi-agent systems** (planner, executor, tools, memory)
> * Clean, minimal, extensible design (no over-engineering)
> * Guardrails are **policy + rule evaluation**, not intelligence
>
> ---
>
> ### 1. Flat Project Structure (Required)
>
> ```
> guardrail-apis/
> ├── main.py
> ├── routes.py
> ├── evaluator.py
> ├── registry.py
> ├── models.py
> ├── rules.py
> ├── policies.py
> ├── config.yaml
> ├── storage.py
> ├── cache.py
> ├── errors.py
> └── utils.py
> ```
>
> No additional folders unless absolutely necessary.
>
> ---
>
> ### 2. Guardrail Model (Must Use)
>
> * **Rule**: atomic, deterministic check
> * **Policy**: named composition of rules
> * **Evaluation Result**: PASS | WARN | FAIL
>
> Aggregation logic:
>
> * FAIL if any rule fails
> * WARN if no fail and at least one warn
> * PASS otherwise
>
> ---
>
> ### 3. Required Guardrail Stages (Multi-Agent)
>
> Guardrails must explicitly support these stages:
>
> ```
> INPUT → PLAN → ACTION → OUTPUT → MEMORY
> ```
>
> ---
>
> ### 4. Classic, Most-Used Rules (Provide IDs & Purpose)
>
> **INPUT**
>
> * no_profanity
> * no_hate_speech
> * pii_detection
> * prompt_injection_check
> * max_input_length
>
> **PLANNING**
>
> * allowed_agent_roles
> * max_plan_steps
> * plan_schema_valid
> * no_recursive_delegation
>
> **ACTION**
>
> * allowed_tools
> * blocked_tools
> * tool_argument_schema_valid
> * max_tool_calls_per_run
> * read_only_mode
>
> **OUTPUT**
>
> * no_pii_leak
> * no_internal_state_exposure
> * max_output_length
> * required_fields_present
>
> **MEMORY**
>
> * memory_write_allowed
> * no_sensitive_data_in_memory
> * memory_scope_enforced
> * memory_size_limit
>
> ---
>
> ### 5. Required Default Policies (Provide YAML)
>
> * user_input_policy
> * planner_agent_policy
> * executor_agent_policy
> * inter_agent_communication_policy
> * agent_output_policy
> * memory_write_policy
>
> Each policy must clearly list which rules it applies.
>
> ---
>
> ### 6. Output Expectations
>
> * Explain the **architecture briefly**
> * List **rules and policies clearly**
> * Keep language **precise and engineering-focused**
> * Avoid AI safety philosophy or vague concepts
>
> The result should be **implementation-ready**, not conceptual.
>
> ---
>
> **Do NOT**:
>
> * Add deep abstractions
> * Introduce plugin systems
> * Add async/event-driven complexity
> * Invent speculative guardrails
>
> Produce a clean, disciplined, production-grade design.

