# Clean Architecture Standard

Every app we build follows Clean Architecture.
Clean Architecture is the engineering standard applied to every project.

## Engineering Principles

Defines the general principles used to guide engineering decisions.

- Prefer simplicity over complexity.
- Prefer explicit behavior over hidden behavior.
- Prefer composition over unnecessary inheritance.
- Prefer small, focused functions and modules.
- Prefer reusable code only when reuse is justified.
- Follow the principle of least surprise.
- Do not overengineer.
- Do not introduce abstractions without a clear need.
- Optimize for maintainability, correctness, security, and testability.

## Architecture Rules

Defines the dependency boundaries and structural responsibilities between layers.

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

Contains the core business logic of the application. It has zero framework dependencies, making it portable, testable, and stable.

- Use cases and application workflows
- Core entities and value objects
- Business rules and validation
- Repository interface contracts
- Domain-level errors and exceptions
- Business logic independent of UI and data sources

## Data Layer

Handles all external data sources and integrations. It provides a controlled boundary between the application and external systems, keeping business logic independent of implementation details.

- Repository implementations
- API clients and service adapters
- Local database and cache handling
- Data models and DTOs
- Data mapping and serialization
- Remote and local data sources
- Third-party service integrations

## Presentation Layer

Responsible for everything related to the user interface and user interaction. It is fully decoupled from business rules so the interface can evolve without affecting domain logic.

- Screens and UI components
- Navigation and routing
- ViewModels and state management
- Responsive and adaptive layouts
- User input handling
- Loading, error, and success states
- User feedback and presentation logic

## Code Quality

Defines expectations for readable, maintainable, and appropriately simple code.

- Write clear, readable, and maintainable code.
- Use descriptive names for variables, functions, classes, and files.
- Avoid single-letter or two-letter variable names unless they are conventional and contextually clear. Prefer clear, descriptive variable names.
- Follow established project patterns, naming conventions, formatting, and architectural conventions. Introduce new patterns only when justified and document them when necessary.
- Use PascalCase for classes, types, and components; camelCase for variables, functions, and methods; UPPER_SNAKE_CASE for constants; and kebab-case for file and directory names unless the language or framework establishes a different convention. Preserve existing project conventions.
- Keep functions and classes focused on a single responsibility.
- Avoid duplicated logic and unnecessary complexity.
- Prefer existing project utilities and dependencies before introducing new ones.
- Remove dead, unused, and obsolete code when safe.
- Keep code simple and easy to understand.
- Comments should explain why, not what; code should be clear and self-documenting.
- Do not duplicate the code in comments or use comments to excuse unclear code.
- If a clear comment cannot be written, reconsider the code's clarity before adding the comment.
- Use comments to clarify intent, context, reasoning, confusing behavior, or intentionally unidiomatic code.
- Keep comments concise, accurate, relevant, and maintainable; comments should dispel confusion, not cause it.
- Include links to the original source of copied code and to useful external references.
- Add comments when fixing non-obvious bugs, especially when documenting their cause or constraints.
- Mark incomplete implementations clearly with markers such as TODO or FIXME and include useful context.
- Do not use emojis in code, comments, documentation, commit messages, or other project content.

## Testing

Defines expectations for meaningful, deterministic, and maintainable test coverage.

- Write tests for important business rules and use cases.
- Test critical application behavior and edge cases.
- Prefer unit tests for Domain Layer logic.
- Add integration tests for important data and service interactions.
- Add UI tests for critical user flows when appropriate.
- Tests should be deterministic and maintainable.
- Do not write tests only to increase coverage numbers.

## Dependency Management

Defines how dependencies are selected, reused, reviewed, and removed.

- Avoid adding dependencies unless they provide clear value.
- Prefer stable and well-maintained libraries.
- Reuse existing dependencies when they already solve the problem.
- Remove unused dependencies.
- Review the impact of dependency changes before adding or upgrading them.

## Configuration

Defines how environment-specific settings are separated, documented, and safely managed.

- Keep environment-specific configuration separate from source code.
- Do not hardcode environment-specific values.
- Use environment variables or the project's established configuration mechanism.
- Provide safe defaults where appropriate.
- Document required configuration.

## Documentation

Defines how documentation stays accurate, useful, and aligned with implementation.

- Keep documentation consistent with the actual implementation.
- Document important architectural decisions and non-obvious behavior.
- Avoid documenting obvious code unnecessarily.
- Update relevant documentation when behavior, architecture, setup, or configuration changes.
- Do not allow documentation to describe functionality that no longer exists.

## Git and Version Control

Defines practices for focused, reviewable, and safe version-control changes.

- Make focused commits with clear messages.
- Avoid committing generated files, secrets, temporary files, or local configuration unless required.
- Keep changes small and reviewable when possible.
- Do not rewrite shared history without a clear reason.
- Review changes before committing.
- Preserve existing Git conventions used by the project.
