---
name: codebase-consistency-audit
description: Audit a project and align code with its existing patterns.
---

# Codebase Consistency Audit

Use this skill when a project contains mixed or inconsistent coding patterns.

## Instructions

1. Inspect the project structure, source code, tests, configuration, and documentation.
2. Identify the patterns used most consistently.
3. Compare inconsistent files against those patterns.
4. Check naming, architecture, imports, error handling, validation, testing, and configuration.
5. Exclude generated files, dependencies, and unrelated changes.
6. Report each inconsistency with its file, current pattern, expected pattern, and priority.
7. Recommend the smallest safe correction.
8. Do not modify files unless the user explicitly requests fix mode.
9. In fix mode, update only confirmed inconsistencies.
10. Check callers, tests, exports, and configuration before editing.
11. Run relevant project checks after changes.
12. Report unresolved conflicts and checks that could not run.

## Rules

- Follow existing project patterns.
- Prefer the dominant pattern over introducing a new one.
- Preserve behavior and public interfaces.
- Do not perform broad rewrites.
- Ask before changing ambiguous patterns.

## Verification

- Run available formatting, lint, type, and test checks.
- Run `git diff --check`.
- Review the final diff for unrelated changes.
