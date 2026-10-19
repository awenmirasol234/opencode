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

## Communication

- Write every response in clear, natural, basic English.
- State the result first.
- Explain only what the user needs to know.
- Use short sentences.
- Use clear headings when helpful.
- Avoid unnecessary technical terms.
- Explain technical terms when necessary.
- State blockers, risks, and next steps clearly.

## Engineering Principles

- Prefer simple, explicit, and unsurprising solutions over clever or hidden behavior.
- Keep functions and modules small and focused.
- Use composition, reuse, and abstractions only when they provide clear value.
- Do not overengineer.
- Optimize for maintainability, correctness, security, and testability.

## Object-Oriented Programming

- Use object-oriented programming when implementing application behavior.
- Model related state and behavior together in focused classes.
- Encapsulate internal state and expose only the operations each class needs.
- Give each class one clear responsibility.
- Prefer composition over inheritance.
- Use interfaces and abstractions at architectural boundaries.
- Do not create classes, inheritance hierarchies, or abstractions without a clear purpose.
- Keep business rules inside domain objects or domain services, not in controllers or UI components.

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

- Place use cases and application workflows in the Domain Layer.
- Place core entities and value objects in the Domain Layer.
- Place business rules and validation in the Domain Layer.
- Place repository interface contracts in the Domain Layer.
- Place domain-level errors and exceptions in the Domain Layer.
- Place business logic independent of UI and data sources in the Domain Layer.

## Data Layer

Place the following in the Data Layer:

- Place repository implementations in the Data Layer.
- Place API clients and service adapters in the Data Layer.
- Place local database and cache handling in the Data Layer.
- Place data models and DTOs in the Data Layer.
- Place data mapping and serialization in the Data Layer.
- Place remote and local data sources in the Data Layer.
- Place third-party service integrations in the Data Layer.

## Presentation Layer

Place the following in the Presentation Layer:

- Place screens and UI components in the Presentation Layer.
- Place navigation and routing in the Presentation Layer.
- Place ViewModels and state management in the Presentation Layer.
- Place responsive and adaptive layouts in the Presentation Layer.
- Place user input handling in the Presentation Layer.
- Place loading, error, and success states in the Presentation Layer.
- Place user feedback and presentation logic in the Presentation Layer.

## Validation

- Validate all untrusted input at system boundaries before processing it.
- Require every field that the use case needs.
- Check input types, formats, lengths, ranges, and allowed values.
- Keep business validation rules in the Domain Layer.
- Sanitize input before storing it or rendering it in a user interface.
- Return clear validation errors without exposing secrets or sensitive data.
- Test valid, invalid, missing, and boundary values.

## Code Quality

- Do not use ternary operators or conditional expressions. Use clear `if`/`else` statements instead.
- Avoid clever one-liners when they make the logic harder to understand. Write clear, readable statements instead.
- Use early returns when they simplify complex business logic.
- Before editing, inspect affected callers, tests, fixtures, configuration, exports, and the current working tree; update every required location and avoid unrelated changes.
- Use basic, readable syntax and straightforward control flow.
- Keep each function, class, and module focused on one responsibility.
- Use clear, descriptive names.
- Avoid single- or two-letter variables unless they are conventional and clear.
- Use `PascalCase` for classes, types, and components.
- Use `camelCase` for variables, functions, and methods.
- Use `UPPER_SNAKE_CASE` for constants.
- Use `kebab-case` for files and directories unless project conventions differ.
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

## Senior-Level Coding Principles

- Handle errors explicitly. Do not silently ignore failures.

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
