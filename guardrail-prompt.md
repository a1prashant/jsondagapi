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

```yaml
openapi: 3.0.3
info:
  title: Guardrail APIs
  description: |
    Guardrail-APIs is a **generic, stateless, enterprise-grade guardrail evaluation service**
    for multi-agent systems.

    Core principles:
    - Caller-authenticated (not agent-authenticated)
    - Stateless, no sessions
    - Policy resolution is server-side
    - Rules are deterministic and auditable
    - Payloads are stage-specific but evaluated generically

  version: "1.0.0"

servers:
  - url: https://guardrails.internal/v1

security:
  - ApiKeyAuth: []

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

  schemas:
    Decision:
      type: string
      enum: [PASS, WARN, FAIL]

    Stage:
      type: string
      enum: [PLAN, ACTION, TOOL, MEMORY, OUTPUT]

    AgentIdentity:
      type: object
      required: [agent_id, instance_id]
      properties:
        agent_id:
          type: string
          description: Logical agent identity (validated against caller)
        instance_id:
          type: string
          description: Runtime-unique agent instance identifier
        agent_tags:
          type: array
          items:
            type: string
          description: Agent capability or classification tags

    EvaluationContext:
      type: object
      additionalProperties: true
      description: Opaque contextual metadata for rule evaluation

    EvaluationRequest:
      type: object
      required: [stage, agent, payload]
      properties:
        stage:
          $ref: '#/components/schemas/Stage'
        agent:
          $ref: '#/components/schemas/AgentIdentity'
        payload:
          oneOf:
            - $ref: '#/components/schemas/PlanPayload'
            - $ref: '#/components/schemas/ActionPayload'
            - $ref: '#/components/schemas/ToolPayload'
            - $ref: '#/components/schemas/MemoryPayload'
            - $ref: '#/components/schemas/OutputPayload'
        context:
          $ref: '#/components/schemas/EvaluationContext'

    RuleResult:
      type: object
      required: [rule_id, decision]
      properties:
        rule_id:
          type: string
        decision:
          $ref: '#/components/schemas/Decision'
        message:
          type: string
        metadata:
          type: object
          additionalProperties: true

    EvaluationResponse:
      type: object
      required: [decision, results]
      properties:
        decision:
          $ref: '#/components/schemas/Decision'
        policy_id:
          type: string
          description: Resolved policy used for evaluation
        results:
          type: array
          items:
            $ref: '#/components/schemas/RuleResult'
        audit_id:
          type: string
          description: Unique identifier for audit/event correlation

    # ---- Stage-specific payloads ----

    PlanPayload:
      type: object
      description: Payload for PLAN-stage evaluation
      required: [plan]
      properties:
        plan:
          type: string
          description: High-level plan or reasoning text

    ActionPayload:
      type: object
      description: Payload for ACTION-stage evaluation
      required: [action]
      properties:
        action:
          type: string
          description: Intended action description

    ToolPayload:
      type: object
      description: Payload for TOOL-stage evaluation
      required: [tool_name]
      properties:
        tool_name:
          type: string
        arguments:
          type: object
          additionalProperties: true

    MemoryPayload:
      type: object
      description: Payload for MEMORY-stage evaluation
      required: [operation]
      properties:
        operation:
          type: string
          enum: [READ, WRITE, DELETE]
        content:
          type: string

    OutputPayload:
      type: object
      description: Payload for OUTPUT-stage evaluation
      required: [output]
      properties:
        output:
          type: string

  responses:
    UnauthorizedError:
      description: Caller authentication failed or agent not allowed

paths:
  /evaluate/plan:
    post:
      summary: Evaluate PLAN-stage intent
      description: |
        Evaluates guardrails for an agent's planning or reasoning step.

        **Intent**: Validate plans before execution.

        **Key inputs**:
        - agent.agent_id, agent.instance_id
        - agent.agent_tags
        - payload.plan

        **Key outputs**:
        - decision (PASS | WARN | FAIL)
        - policy_id (server-resolved)
        - audit_id
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              allOf:
                - $ref: '#/components/schemas/EvaluationRequest'
                - type: object
                  properties:
                    stage:
                      enum: [PLAN]
      responses:
        '200':
          description: PLAN evaluation result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvaluationResponse'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

  /evaluate/action:
    post:
      summary: Evaluate ACTION-stage intent
      description: |
        Evaluates guardrails before an agent performs an action.

        **Intent**: Prevent unsafe or unauthorized actions.

        **Key inputs**:
        - agent.agent_id, agent.instance_id
        - agent.agent_tags
        - payload.action

        **Key outputs**:
        - decision
        - policy_id
        - audit_id
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              allOf:
                - $ref: '#/components/schemas/EvaluationRequest'
                - type: object
                  properties:
                    stage:
                      enum: [ACTION]
      responses:
        '200':
          description: ACTION evaluation result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvaluationResponse'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

  /evaluate/tool:
    post:
      summary: Evaluate TOOL invocation intent
      description: |
        Evaluates guardrails before an agent invokes a tool.

        **Intent**: Enforce tool allow/deny, argument checks, and rate limits.

        **Key inputs**:
        - agent identity
        - payload.tool_name
        - payload.arguments

        **Key outputs**:
        - decision
        - policy_id
        - audit_id
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              allOf:
                - $ref: '#/components/schemas/EvaluationRequest'
                - type: object
                  properties:
                    stage:
                      enum: [TOOL]
      responses:
        '200':
          description: TOOL evaluation result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvaluationResponse'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

  /evaluate/memory:
    post:
      summary: Evaluate MEMORY access intent
      description: |
        Evaluates guardrails for memory read/write/delete operations.

        **Intent**: Protect sensitive data and memory integrity.

        **Key inputs**:
        - agent identity
        - payload.operation
        - payload.content

        **Key outputs**:
        - decision
        - policy_id
        - audit_id
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              allOf:
                - $ref: '#/components/schemas/EvaluationRequest'
                - type: object
                  properties:
                    stage:
                      enum: [MEMORY]
      responses:
        '200':
          description: MEMORY evaluation result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvaluationResponse'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

  /evaluate/output:
    post:
      summary: Evaluate OUTPUT emission intent
      description: |
        Evaluates guardrails before an agent emits final output.

        **Intent**: Enforce safety, compliance, and formatting rules.

        **Key inputs**:
        - agent identity
        - payload.output

        **Key outputs**:
        - decision
        - policy_id
        - audit_id
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              allOf:
                - $ref: '#/components/schemas/EvaluationRequest'
                - type: object
                  properties:
                    stage:
                      enum: [OUTPUT]
      responses:
        '200':
          description: OUTPUT evaluation result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvaluationResponse'
        '401':
          $ref: '#/components/responses/UnauthorizedError'

  /policies:
    get:
      summary: List configured guardrail policies
      description: |
        Administrative / internal endpoint that lists all configured guardrail
        policies available in the system.

        **Key outputs**:
        - policy identifiers
        - associated rule lists
        - policy execution mode (strict / permissive)

        This endpoint is intended for:
        - governance review
        - debugging
        - platform tooling
      security:
        - ApiKeyAuth: []
      responses:
        '200':
          description: List of configured policies

  /rules:
    get:
      summary: List registered guardrail rules
      description: |
        Administrative / internal endpoint that exposes all rule identifiers
        currently registered with the guardrail engine.

        **Key outputs**:
        - rule_id: Unique rule identifiers

        Used for:
        - policy authoring
        - validation
        - governance visibility
      security:
        - ApiKeyAuth: []
      responses:
        '200':
          description: List of registered rules


```

