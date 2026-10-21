---
name: clean-architecture-standards
description: Apply Clean Architecture and consistent project engineering standards.
---

# Clean Architecture Standards

Use this skill when implementing or reviewing project changes.

## Instructions

1. Inspect the project structure, affected files, callers, tests, fixtures, exports, configuration, and Git status.
2. Keep dependencies pointing toward the Domain Layer.
3. Keep domain logic independent from UI, frameworks, databases, and external services.
4. Place business rules, use cases, entities, value objects, and repository contracts in the Domain Layer.
5. Place repositories, data sources, DTOs, mappings, APIs, and integrations in the Data Layer.
6. Place screens, components, navigation, state, input handling, and presentation states in the Presentation Layer.
7. Keep each class, function, and module focused on one responsibility.
8. Use composition and stable interfaces instead of unnecessary inheritance or abstractions.
9. Validate untrusted input at system boundaries and test valid, invalid, missing, and boundary values.
10. Use clear names, simple control flow, early returns, and explicit `if`/`else` statements.
11. Use `PascalCase` for classes, types, and components; `camelCase` for variables and functions; and `UPPER_SNAKE_CASE` for constants.
12. Reuse existing utilities, dependencies, patterns, and configuration.
13. Preserve existing behavior and public interfaces.
14. Protect secrets and keep environment-specific values outside source code.
15. Add focused tests for business rules, use cases, critical behavior, and edge cases.
16. Keep documentation consistent with implementation and record important decisions.
17. Avoid unrelated changes, broad rewrites, dead code, unnecessary dependencies, and clever one-liners.
18. Do not use emojis in code, comments, documentation, or commit messages.
19. Ask before changing ambiguous architecture, behavior, or project conventions.
20. Run relevant project checks and report unavailable checks instead of inventing commands.

## Verification

- Run relevant tests, linting, formatting, and type checks.
- Run `git diff --check`.
- Review the final diff for unrelated changes, exposed secrets, and broken boundaries.
