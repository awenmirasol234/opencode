# Agent Index

## Purpose

Quick routing reference for `Engineering-Lead`. Use this index to select the smallest appropriate specialist. It summarizes routing only and does not replace any agent's full instructions.

## Primary Agent Structure

The primary agents are independent peers:

```text
Primary Agents
├── Engineering-Lead
├── Plan
└── Build
```

Only `Engineering-Lead` has specialized subagents:

```text
Engineering-Lead
├── Software-Engineer
├── Frontend-Engineer
├── Backend-Engineer
├── QA-Engineer
└── Security-Engineer
```

`Plan` and `Build` are primary agents, not children of `Engineering-Lead`.

## Specialist Directory

### Software-Engineer

- **Main responsibility:** General implementation and cross-cutting engineering work.
- **Use when:** The task does not have a clear frontend, backend, QA, or security owner.
- **Do not use when:** A more specific specialist clearly owns the work.

### Frontend-Engineer

- **Main responsibility:** UI, UX implementation, accessibility, responsiveness, and client-side behavior.
- **Use when:** The task primarily affects frontend components, user flows, browser behavior, or client-side state.
- **Do not use when:** The change is primarily backend, testing, security, or a trivial isolated UI edit.

### Backend-Engineer

- **Main responsibility:** APIs, business logic, server-side behavior, and integrations.
- **Use when:** The task primarily affects services, API contracts, backend workflows, or server integrations.
- **Do not use when:** The task is primarily frontend, testing, or security-specific.

### QA-Engineer

- **Main responsibility:** Test strategy, test cases, regression testing, and verification.
- **Use when:** Broad test coverage, regression analysis, edge cases, or independent verification is needed.
- **Do not use when:** The implementing specialist can add and run straightforward tests as part of the change.

### Security-Engineer

- **Main responsibility:** Authentication, authorization, secrets, validation, dependency risks, and security reviews.
- **Use when:** The task affects security boundaries, sensitive data, credentials, public interfaces, or security controls.
- **Do not use when:** The task has no meaningful security impact.

## Routing Rules

1. Use the smallest number of specialists necessary.
2. Prefer one specialist whenever possible.
3. Do not call a specialist when `Engineering-Lead` can handle the coordination or decision directly.
4. Select the specialist that owns the task's dominant concern.
5. Avoid overlapping specialists and duplicated work.
6. Use multiple specialists only when the task genuinely crosses separate domains.
7. Sequence specialists when their work affects the same files or depends on earlier results.
8. Do not create new specialists without a recurring, distinct, and justified need.
9. Keep specialist requests scoped to a clear outcome and verification requirement.

## Common Task Routing

| Task | Route |
|---|---|
| General feature or cross-cutting change | `Software-Engineer` |
| UI, component, accessibility, or browser behavior | `Frontend-Engineer` |
| API, business logic, service, or integration work | `Backend-Engineer` |
| Test strategy, regression coverage, or verification | `QA-Engineer` |
| Authentication, authorization, secrets, or security review | `Security-Engineer` |

## Escalation Rules

- For a task spanning multiple domains, identify one primary specialist and add only the necessary supporting specialist.
- Have specialists communicate through `Engineering-Lead`; they must not delegate directly to one another.
- Keep file ownership distinct when multiple specialists are used.
- Return unresolved scope, design, or risk decisions to `Engineering-Lead`.
- `Engineering-Lead` remains responsible for coordination, scope, sequencing, and final decisions.

## Agent Constraints

- `Engineering-Lead` is the only primary agent that can delegate to specialized subagents.
- `Plan` has no subagents and must not use or spawn them.
- `Build` has no subagents and must not use or spawn them.
- Every specialist has no subagents and must not spawn additional agents.
- Specialists must not delegate to one another directly.
- `Plan` and `Build` remain independent peer-level primary agents.
