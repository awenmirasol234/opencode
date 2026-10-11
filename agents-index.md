# Plan Routing Index

Use the smallest suitable specialist. Read the selected agent's full instructions before delegating.

## Primary Agents

These are peer-level, independently selectable agents:

- `Plan` — the primary planning and coordination mode: explores, clarifies requirements, assesses risks, delegates focused tasks when needed, and produces an implementation plan; must not edit project files.
- `Build` — the primary implementation mode: makes scoped changes directly after requirements are clear; must not use subagents.

Only `Plan` may launch the specialized subagents below.

## Plan Specialized Subagents

| Agent | Route when the task is mainly about... |
|---|---|
| `Technical-Analyst` | Deeper read-only analysis of requirements, architecture, dependencies, impact, risks, or tradeoffs when the lead needs specialist evidence before implementation |
| `Generalist-Engineer` | Delegated implementation of general, cross-cutting, or unclear-domain work when the lead has chosen to delegate rather than use Build |
| `Frontend-Engineer` | Browser/client behavior, UI, UX, accessibility, or responsiveness |
| `Backend-Engineer` | APIs, server behavior, business logic, services, or integrations |
| `Test-Engineer` | Test strategy, regression coverage, edge cases, or focused verification |
| `Application-Security-Engineer` | Authentication, authorization, secrets, validation, sensitive data, or application security risks |
| `Database-Engineer` | Schemas, migrations, queries, indexes, transactions, or data integrity |
| `DevOps-Engineer` | Docker, CI/CD, deployment, infrastructure, environments, or monitoring |

## Routing Rules

1. Clarify scope or requirements when needed.
2. Use `Technical-Analyst` first when requirements or architecture need analysis before implementation.
3. Choose one dominant implementation specialist; use `Generalist-Engineer` for cross-cutting or unclear work.
4. For cross-domain work, choose one primary specialist and the smallest necessary support.
5. Use `Test-Engineer` when verification needs dedicated strategy or coverage; routine tests stay with the implementer.
6. Run specialists in parallel only when ownership is disjoint, neither needs the other's output, and verification is independent; normally use no more than two.
7. Sequence dependent work and never parallelize edits to shared files.
8. Assign explicit scope, ownership, must-not-change boundaries, and verification requirements.
9. Keep delegation one level deep: `Plan` → specialist.
10. Plan should handle a task directly when it is limited to clarification, sequencing, lightweight read-only investigation, or review. It may delegate implementation and specialist analysis when needed, but it does not edit project files.

Specialized subagents report through `Plan`, must not spawn subagents, and must not expand beyond their assigned scope. `Technical-Analyst` is read-only and does not implement changes.
