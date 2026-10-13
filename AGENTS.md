# Clean Architecture Standard

Every app follows Clean Architecture, which is the engineering standard for all projects.

## Clarification and Questions

- Ask the user for clarification with the `question` tool when a task, requirement, constraint, desired behavior, or significant implementation decision is unclear.
- Do not make assumptions about uncertain requirements. Explain what needs clarification and offer concise options.
- Proceed without asking only for low-risk details that are unambiguous from the request or established project conventions.
- Confirm destructive or irreversible actions with the user before executing them.

## Tool Usage

- Use `read` to inspect files, `glob` to find paths, and `grep` to search contents.
- Use `patch` to create, update, or delete files.
- Use `shell` to run project commands and verification checks. Prefer dedicated file tools for file operations.
- Use `webfetch` to retrieve a known web page and `websearch` to find current external information.
- Use `skill` when a task matches an available specialized skill, `subagent` when delegation is appropriate, and `execute` to combine independent tool calls.
- Use session, worktree, and MCP tools only when they are available and relevant.

## Engineering Principles

- Prefer simple, explicit, unsurprising solutions over clever or hidden behavior.
- Keep functions and modules small and focused. Use composition, reuse, and abstractions only when justified.
- Do not overengineer.
- Optimize for maintainability, correctness, security, and testability.

## Architecture Rules

- Dependencies must point inward toward the Domain Layer, which must not depend on the Presentation or Data Layer.
- The Presentation Layer must not access external data sources directly.
- The Data Layer must implement repository contracts defined by the Domain Layer.
- Business rules belong in the Domain Layer, and framework-specific code must remain outside it.
- Each layer must have a clear and limited responsibility.
- Changes in UI, APIs, databases, or external services should not require changes to core business rules.
- Keep modules loosely coupled and highly cohesive. Depend on stable abstractions rather than concrete implementations, and minimize unrelated knowledge.

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

- Write clear, simple, readable, maintainable, and beginner-friendly code with straightforward control flow.
- Use descriptive names; avoid single- or two-letter variables unless conventional and clear.
- Use `PascalCase` for classes, types, and components; `camelCase` for variables, functions, and methods; `UPPER_SNAKE_CASE` for constants; and `kebab-case` for files and directories unless project conventions differ.
- Follow established project patterns, formatting, naming, and architectural conventions.
- Keep functions and classes focused; avoid duplication and unnecessary abstractions.
- Prefer existing utilities and dependencies. Remove dead code when safe.
- Use concise, accurate comments to explain intent, reasoning, or non-obvious behavior—not what the code already shows. Do not duplicate code in comments or use them to excuse unclear code.
- Link copied code and useful external references. Mark incomplete work with `TODO` or `FIXME`.
- Do not use emojis in code, comments, documentation, or commit messages.

## Testing

- Test important business rules, use cases, critical behavior, and edge cases.
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

- Add dependencies only when they provide clear value. Prefer stable, well-maintained libraries and reuse existing dependencies when they solve the problem.
- Remove unused dependencies.
- Review the impact of dependency changes before adding or upgrading them.

## Configuration

- Keep environment-specific configuration separate from source code; do not hardcode environment-specific values.
- Use environment variables or the project's established configuration mechanism.
- Provide safe defaults where appropriate.
- Document required configuration.

## Security

- Never expose, commit, or copy secrets, credentials, or sensitive configuration. Keep sensitive local configuration ignored and environment-specific.
- Treat external input and configuration as untrusted at system boundaries.

## Documentation

- Keep documentation consistent with the implementation; update or remove outdated content.
- Document important architectural decisions and non-obvious behavior.
- Avoid documenting obvious code unnecessarily.
- Update relevant documentation when behavior, architecture, setup, or configuration changes.

## Git and Version Control

- Make focused commits with clear messages and keep changes small and reviewable.
- Avoid committing generated files, secrets, temporary files, or local configuration unless required.
- Do not rewrite shared history without a clear reason.
- Review changes before committing.
- Preserve existing Git conventions used by the project.
