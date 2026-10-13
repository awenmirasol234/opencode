# Clean Architecture Standard

Every app we build follows Clean Architecture.
Clean Architecture is the engineering standard applied to every project.

## Engineering Principles

- Prefer simplicity over complexity.
- Prefer explicit behavior over hidden behavior.
- Prefer composition over unnecessary inheritance.
- Prefer small, focused functions and modules.
- Prefer reusable code only when reuse is justified.
- Follow the principle of least surprise.
- Do not overengineer.
- Do not introduce abstractions without a clear need.
- Optimize for maintainability, correctness, security, and testability.

## Clarification and Questions

- Whenever requirements, scope, constraints, desired behavior, or a significant implementation decision is unclear, use the available ask-question tool to ask the user before proceeding.
- Do not guess about material ambiguities. Explain the decision that is needed and offer concise options where appropriate.
- Proceed without asking only for low-risk details that are unambiguous from the request or established project conventions.
- Confirm destructive or irreversible actions with the user before executing them.

## Architecture Rules

- Dependencies must point inward toward the Domain Layer.
- The Domain Layer must not depend on the Presentation or Data Layer.
- The Presentation Layer must not access external data sources directly.
- The Data Layer must implement repository contracts defined by the Domain Layer.
- Business rules must remain inside the Domain Layer.
- Framework-specific code must remain outside the Domain Layer.
- Each layer must have a clear and limited responsibility.
- Changes in UI, APIs, databases, or external services should not require changes to core business rules.
- Keep modules loosely coupled and highly cohesive. Depend on stable abstractions rather than concrete implementations, and minimize knowledge shared between unrelated modules.

## Domain Layer

- Use cases and application workflows
- Core entities and value objects
- Business rules and validation
- Repository interface contracts
- Domain-level errors and exceptions
- Business logic independent of UI and data sources

## Data Layer

- Repository implementations
- API clients and service adapters
- Local database and cache handling
- Data models and DTOs
- Data mapping and serialization
- Remote and local data sources
- Third-party service integrations

## Presentation Layer

- Screens and UI components
- Navigation and routing
- ViewModels and state management
- Responsive and adaptive layouts
- User input handling
- Loading, error, and success states
- User feedback and presentation logic

## Code Quality

- Write clear, simple, readable, and maintainable code.
- Use descriptive names; avoid single- or two-letter variables unless conventional and clear.
- Use `PascalCase` for classes, types, and components; `camelCase` for variables, functions, and methods; `UPPER_SNAKE_CASE` for constants; and `kebab-case` for files and directories unless project conventions differ.
- Follow established project patterns, formatting, naming, and architectural conventions.
- Keep functions and classes focused; avoid duplication and unnecessary abstractions.
- Prefer existing utilities and dependencies. Remove dead code when safe.
- Comments should explain why, not what. Keep them concise, accurate, and useful.
- Use comments for intent, reasoning, confusing or unidiomatic code, and non-obvious bug fixes.
- Do not duplicate code in comments or use comments to excuse unclear code.
- Link copied code and useful external references. Mark incomplete work with `TODO` or `FIXME`.
- Do not use emojis in code, comments, documentation, or commit messages.

## Testing

- Write tests for important business rules and use cases.
- Test critical application behavior and edge cases.
- Prefer unit tests for Domain Layer logic.
- Add integration tests for important data and service interactions.
- Add UI tests for critical user flows when appropriate.
- Tests should be deterministic and maintainable.
- Do not write tests only to increase coverage numbers.

## Verification

- Run available project checks relevant to the change.
- For documentation or configuration changes, run targeted validation such as `git diff --check`.
- Report checks that are unavailable rather than inventing commands.

## Dependency Management

- Avoid adding dependencies unless they provide clear value.
- Prefer stable and well-maintained libraries.
- Reuse existing dependencies when they already solve the problem.
- Remove unused dependencies.
- Review the impact of dependency changes before adding or upgrading them.

## Configuration

- Keep environment-specific configuration separate from source code.
- Do not hardcode environment-specific values.
- Use environment variables or the project's established configuration mechanism.
- Provide safe defaults where appropriate.
- Document required configuration.

## Security

- Never expose, commit, or copy secrets, credentials, or sensitive configuration.
- Keep sensitive local configuration ignored and environment-specific.
- Treat external input and configuration as untrusted at system boundaries.

## Documentation

- Keep documentation consistent with the actual implementation.
- Document important architectural decisions and non-obvious behavior.
- Avoid documenting obvious code unnecessarily.
- Update relevant documentation when behavior, architecture, setup, or configuration changes.
- Do not allow documentation to describe functionality that no longer exists.

## Git and Version Control

- Make focused commits with clear messages.
- Avoid committing generated files, secrets, temporary files, or local configuration unless required.
- Keep changes small and reviewable when possible.
- Do not rewrite shared history without a clear reason.
- Review changes before committing.
- Preserve existing Git conventions used by the project.
