# Clean Architecture Standard

Use Clean Architecture as the engineering standard for every app.

## Clarification and Questions

- Ask the user for clarification with the `question` tool when a task, requirement, constraint, desired behavior, or significant implementation decision is unclear.
- Do not make assumptions about uncertain requirements. Explain what needs clarification and offer concise options.
- Proceed without asking only when details are low-risk, unambiguous, or established by project conventions.
- Confirm destructive or irreversible actions with the user before executing them.

## Tool Usage

- Use `read` to inspect files.
- Use `glob` to find paths.
- Use `grep` to search contents.
- Use `patch` to create, update, or delete files.
- Use `shell` to run project commands and verification checks.
- Prefer dedicated file tools over shell commands for file operations.
- Use `webfetch` to retrieve known web pages.
- Use `websearch` to find current external information.
- Use `skill` when a task matches an available specialized skill.
- Use `subagent` when delegation is appropriate.
- Use `execute` to combine independent tool calls.
- Use session, worktree, and MCP tools only when they are available and relevant.

## Engineering Principles

- Prefer simple, explicit, and unsurprising solutions over clever or hidden behavior.
- Keep functions and modules small and focused.
- Use composition, reuse, and abstractions only when they provide clear value.
- Do not overengineer.
- Optimize for maintainability, correctness, security, and testability.

## Architecture Rules

- Point dependencies inward toward the Domain Layer.
- Keep the Domain Layer independent of the Presentation and Data Layers.
- Prevent the Presentation Layer from accessing external data sources directly.
- Implement Domain Layer repository contracts in the Data Layer.
- Keep business rules in the Domain Layer.
- Keep framework-specific code outside the Domain Layer.
- Give each layer a clear and limited responsibility.
- Ensure that UI, API, database, and external-service changes do not require changes to core business rules.
- Keep modules loosely coupled and highly cohesive.
- Depend on stable abstractions rather than concrete implementations.
- Minimize unrelated knowledge between modules.

## Domain Layer

Place the following in the Domain Layer:

- Use cases and application workflows
- Core entities and value objects
- Business rules and validation
- Repository interface contracts
- Domain-level errors and exceptions
- Business logic independent of UI and data sources

## Data Layer

Place the following in the Data Layer:

- Repository implementations
- API clients and service adapters
- Local database and cache handling
- Data models and DTOs
- Data mapping and serialization
- Remote and local data sources
- Third-party service integrations

## Presentation Layer

Place the following in the Presentation Layer:

- Screens and UI components
- Navigation and routing
- ViewModels and state management
- Responsive and adaptive layouts
- User input handling
- Loading, error, and success states
- User feedback and presentation logic

## Code Quality

- Write the simplest code that correctly solves the problem.
- Prefer basic, readable syntax and straightforward control flow.
- Prefer clear, explicit solutions over clever, advanced, or overly abstract implementations.
- Keep each function, class, and module focused on one responsibility.
- Use clear, descriptive names.
- Avoid single- or two-letter variables unless they are conventional and clear.
- Use `PascalCase` for classes, types, and components.
- Use `camelCase` for variables, functions, and methods.
- Use `UPPER_SNAKE_CASE` for constants.
- Use `kebab-case` for files and directories unless project conventions differ.
- Avoid unnecessary abstractions, design patterns, wrappers, helper functions, and dependencies.
- Add abstractions only when they provide clear value.
- Reuse existing utilities, dependencies, and implementations when appropriate.
- Remove dead code when safe.
- Avoid deeply nested conditions and unnecessarily complex logic.
- Follow the existing project architecture, patterns, formatting, naming, and conventions.
- Preserve existing functionality.
- Avoid unrelated changes.
- Add concise comments only when they explain non-obvious behavior or reasoning.
- Do not repeat code in comments.
- Do not use comments to excuse unclear code.
- Link copied code and useful external references.
- Mark incomplete work with `TODO` or `FIXME`.
- Do not use emojis in code, comments, documentation, or commit messages.

## Testing

- Test important business rules, use cases, critical behavior, and edge cases.
- Prefer unit tests for Domain Layer logic.
- Add integration tests for important data and service interactions.
- Add UI tests for critical user flows when appropriate.
- Write deterministic and maintainable tests.
- Do not write tests solely to increase coverage numbers.

## Verification

- Run the project checks relevant to the change.
- For documentation or configuration changes, run targeted validation such as `git diff --check`.
- Report unavailable checks instead of inventing commands.

## Dependency Management

- Add dependencies only when they provide clear value.
- Prefer stable, well-maintained libraries.
- Reuse existing dependencies when they solve the problem.
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

- Keep documentation consistent with the implementation.
- Update or remove outdated documentation.
- Document important architectural decisions and non-obvious behavior.
- Avoid documenting obvious code unnecessarily.
- Update relevant documentation when behavior, architecture, setup, or configuration changes.

## Git and Version Control

- Make focused commits with clear messages.
- Keep changes small and reviewable.
- Avoid committing generated files, secrets, temporary files, or local configuration unless required.
- Do not rewrite shared history without a clear reason.
- Review changes before committing.
- Preserve existing Git conventions used by the project.
