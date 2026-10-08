# Clean Architecture Standard

Every app we build follows Clean Architecture.
Clean Architecture is the engineering standard applied to every project.

## Presentation Layer

Responsible for everything related to the user interface and user interaction. It is fully decoupled from business rules so the interface can evolve without affecting domain logic.

- Screens and UI components
- Navigation and routing
- ViewModels and state management
- Responsive and adaptive layouts
- User input handling
- Loading, error, and success states
- User feedback and presentation logic

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

## Architecture Rules

- Dependencies must point inward toward the Domain Layer.
- The Domain Layer must not depend on the Presentation or Data Layer.
- The Presentation Layer must not access external data sources directly.
- The Data Layer must implement repository contracts defined by the Domain Layer.
- Business rules must remain inside the Domain Layer.
- Framework-specific code must remain outside the Domain Layer.
- Each layer must have a clear and limited responsibility.
- Changes in UI, APIs, databases, or external services should not require changes to core business rules.
