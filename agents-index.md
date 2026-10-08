# Engineering-Lead Agent Index

Quick routing reference. Use the smallest suitable specialist; consult full agent instructions for execution details.

## Structure

```text
Primary Agents
├── Engineering-Lead
├── Plan
└── Build

Engineering-Lead specialists
├── Software-Engineer
├── Frontend-Engineer
├── Backend-Engineer
├── QA-Engineer
├── Security-Engineer
├── Database-Engineer
└── DevOps-Engineer
```

`Engineering-Lead`, `Plan`, and `Build` are independently selectable primary agents. Only `Engineering-Lead` can delegate to specialists.

## Specialist Routing

| Specialist | Use for | Avoid when |
|---|---|---|
| `Software-Engineer` | General implementation and cross-cutting work | A domain specialist clearly owns the task |
| `Frontend-Engineer` | UI, UX, accessibility, responsiveness, and client behavior | The task is mainly backend, testing, or security |
| `Backend-Engineer` | APIs, business logic, services, and integrations | The task is mainly frontend, testing, or security |
| `QA-Engineer` | Test strategy, regression coverage, edge cases, and verification | The implementer can add straightforward tests |
| `Security-Engineer` | Authentication, authorization, secrets, validation, and security risks | The task has no meaningful security impact |
| `Database-Engineer` | Schemas, migrations, queries, indexes, and data integrity | The database change is trivial and low-risk |
| `DevOps-Engineer` | Docker, CI/CD, deployment, infrastructure, and monitoring | The configuration change is routine and low-risk |

## Routing Rules

- Do not delegate when no specialist adds clear value; for implementation work, use `Software-Engineer` unless another specialist clearly owns it.
- Prefer one specialist and select the task's dominant domain.
- Prefer `Frontend-Engineer` for browser and client behavior, `Backend-Engineer` for server and API behavior, and `Software-Engineer` for cross-cutting or unclear ownership.
- Use multiple specialists only for genuinely separate concerns; sequence dependent work.
- Run independent workstreams concurrently only when ownership is disjoint, neither needs the other's output, and verification can proceed independently; normally use no more than two in parallel.
- Avoid overlapping work, conflicting edits, and unnecessary delegation.
- Add specialists only for recurring, distinct, and justified needs.
- Keep delegation one level deep: `Engineering-Lead` → specialist.

## Escalation and Constraints

- `Engineering-Lead` owns scope, coordination, sequencing, and final decisions.
- For cross-domain work, choose one primary specialist and the smallest necessary support.
- Specialists communicate through `Engineering-Lead` and cannot delegate to one another.
- `Plan` and `Build` are independent primary agents with no subagents.
- Specialists have no subagents and must not spawn additional agents.
