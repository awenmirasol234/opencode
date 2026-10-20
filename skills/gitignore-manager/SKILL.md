---
name: gitignore-manager
description: Create, update, or refresh project-specific .gitignore files and useful .dockerignore files.
---

# Gitignore Manager

Use this skill when a project needs a missing, incomplete, incorrect, or stale `.gitignore` file. Use it when a Docker project also needs a project-specific `.dockerignore` file.

Do not modify unrelated configuration. Do not delete files. Do not untrack files that are already tracked by Git. Ask the user when the project purpose or the effect of a potentially risky rule is unclear.

## Workflow

### 1. Inspect the project

- Identify the project root and any nested project or repository roots.
- Inspect source directories, test directories, scripts, documentation, configuration files, package manifests, lockfiles, build tools, and deployment files.
- Identify the programming languages, frameworks, package managers, runtimes, and development tools actually used.
- Look for generated directories and files already present in the project.
- Detect Dockerfiles, Compose files, build contexts, and related deployment configuration.
- Read the existing `.gitignore` and `.dockerignore` files before changing them.

### 2. Check Git state

- Run `git status --short` from the repository root.
- Run `git ls-files` when tracking status affects the decision.
- Identify ignored files, tracked generated files, and untracked files that may be important.
- Remember that changing `.gitignore` does not untrack files already committed or staged.
- Report tracked files that match a new ignore rule. Do not remove them from Git automatically.

### 3. Classify files to ignore

Add rules only for files the project actually creates or uses locally. Consider these categories:

- Dependencies installed from package managers.
- Build output, coverage output, generated code, and compiled artifacts.
- Tool caches, test caches, temporary files, and local runtime state.
- Logs, crash reports, and local databases when they are not project assets.
- Local environment files, credentials, tokens, certificates, private keys, and other secrets.
- IDE metadata and operating-system files.
- Local deployment data, Docker volumes, and development-only artifacts when appropriate.

Preserve source code, tests, documentation, assets, migration files, configuration required to build or run the project, deployment files, and dependency lockfiles. Preserve safe example files such as `.env.example`.

### 4. Decide `.gitignore` rules

- Create `.gitignore` when it is missing and the project has files that should not be committed.
- Update an existing `.gitignore` when required rules are missing or incorrect.
- Refresh an existing `.gitignore` by removing duplicate, obsolete, irrelevant, or overly broad rules.
- Preserve valid existing rules unless they conflict with the actual project or hide important files.
- Use clear section headings when they improve readability.
- Prefer a specific path or filename over a broad wildcard.
- Add framework or tool rules only when inspection confirms that the project uses that framework or tool.
- Ignore real secret files, but do not ignore safe templates or examples required by the project.
- Do not ignore lockfiles unless the project explicitly requires that behavior.
- Do not use rules that could hide source, documentation, fixtures, migrations, deployment files, or required configuration.

### 5. Decide `.dockerignore` rules

- Create or update `.dockerignore` only when Docker is used and excluding files provides a meaningful benefit.
- Determine each Docker build context from the Dockerfile, Compose file, and build configuration.
- Read every relevant Dockerfile and inspect `COPY` and `ADD` instructions.
- Preserve every file required by the Docker build, including manifests, lockfiles, application source, build configuration, scripts, certificates intentionally used by the image, and files copied from the build context.
- Exclude dependencies, host build output, tests, documentation, local environment files, secrets, caches, logs, IDE files, and unrelated files only when the image does not need them.
- Treat `.gitignore` and `.dockerignore` as separate files with separate purposes. Do not copy all rules between them.
- Account for multiple Dockerfiles, Compose services, and different build contexts.
- Do not create `.dockerignore` when Docker is absent or when it would not reduce unnecessary build context.

### 6. Apply the smallest safe change

- Create only the required ignore files.
- Keep rules concise, readable, and grouped by purpose.
- Remove exact duplicates and rules that clearly have no relation to the project.
- Keep rules that protect secrets or prevent accidental generated-file commits unless inspection proves they are wrong.
- Avoid broad patterns such as ignoring an entire source, configuration, or deployment directory.
- Do not delete project files, modify unrelated configuration, or change tracked-file state.
- Explain any rule whose effect is not obvious or whose safety depends on a project convention.

## Decision rules

- Base every rule on observed project contents, configuration, or a documented project convention.
- Prefer no rule over a speculative rule.
- Preserve an existing rule when its purpose is unclear unless it is demonstrably harmful; ask the user when removal could hide or expose files.
- Keep generated files out of Git and unnecessary files out of Docker build contexts.
- Treat environment files and credentials as untrusted sensitive data.
- Never assume that a generic language template matches the project.
- Never claim that a file is untracked merely because it is ignored.

## Verification checklist

- [ ] Confirm that the project structure and actual tools were inspected.
- [ ] Confirm that existing `.gitignore` and `.dockerignore` files were read first.
- [ ] Confirm that source, documentation, lockfiles, required configuration, and deployment files remain eligible for tracking or Docker inclusion when needed.
- [ ] Confirm that secrets and machine-specific files are ignored without ignoring safe examples.
- [ ] Confirm that no unnecessary framework or tool patterns were added.
- [ ] Confirm that Dockerfile `COPY` and `ADD` requirements are not excluded.
- [ ] Run `git check-ignore -v --no-index` for representative files that should be ignored and preserved.
- [ ] Run `git status --short` and inspect the result for unexpected changes.
- [ ] Run `git diff --check`.
- [ ] Confirm that no files were deleted and no tracked files were untracked.
- [ ] Report checks that could not be run and any tracked files that still require manual untracking.
