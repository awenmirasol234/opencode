# Engineering-Lead Routing Index

Use the smallest suitable specialist. Read the selected agent's full instructions before delegating.

## Primary Agents

These are peer-level, independently selectable agents:

- `Engineering-Lead` — owns scope, coordination, delegation, sequencing, and final decisions.
- `Plan` — plans and explores; must not use subagents.
- `Build` — implements directly; must not use subagents.

Only `Engineering-Lead` may launch the specialized subagents below.

## Engineering-Lead Specialized Subagents

| Agent | Route when the task is mainly about... |
|---|---|
| `Software-Engineer` | General implementation, cross-cutting work, or unclear ownership |
| `Frontend-Engineer` | Browser/client behavior, UI, UX, accessibility, or responsiveness |
| `Backend-Engineer` | APIs, server behavior, business logic, services, or integrations |
| `QA-Engineer` | Test strategy, regression coverage, edge cases, or focused verification |
| `Security-Engineer` | Authentication, authorization, secrets, validation, sensitive data, or security risks |
| `Database-Engineer` | Schemas, migrations, queries, indexes, transactions, or data integrity |
| `DevOps-Engineer` | Docker, CI/CD, deployment, infrastructure, environments, or monitoring |

## Routing Rules

1. Clarify scope or requirements when needed.
2. Choose one dominant specialist; use `Software-Engineer` for cross-cutting or unclear work.
3. For cross-domain work, choose one primary specialist and the smallest necessary support.
4. Use `QA-Engineer` when verification needs dedicated strategy or coverage; routine tests stay with the implementer.
5. Run specialists in parallel only when ownership is disjoint, neither needs the other's output, and verification is independent; normally use no more than two.
6. Sequence dependent work and never parallelize edits to shared files.
7. Assign explicit scope, ownership, must-not-change boundaries, and verification requirements.
8. Keep delegation one level deep: `Engineering-Lead` → specialist.

Specialized subagents report through `Engineering-Lead`, must not spawn subagents, and must not expand beyond their assigned scope.
