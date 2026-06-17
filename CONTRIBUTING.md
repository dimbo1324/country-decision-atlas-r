# Contributing

Country Decision Atlas is being prepared as a monorepo for a relocation and
country-decision product. The repository should stay easy to scan, easy to run
locally, and safe for future contributors.

## Development Principles

- Keep product code inside `apps/*` and shared code inside `packages/*`.
- Keep infrastructure code inside `infra`, root config files, and `.github`.
- Do not commit secrets, local dumps, generated exports, or personal research
  workspaces.
- Keep changes small enough to review. Prefer explicit names over clever
  abstractions.
- Treat country, migration, legal, safety, and cost-of-living data as sourced
  data. Store provenance and timestamps when adding data pipelines.

## Branches and Commits

- Use short feature branches for normal work.
- Prefer clear commit messages in the imperative mood, for example
  `Add country scoring baseline`.
- Run formatting, linting, and tests before opening a pull request.

## Pull Requests

A pull request should include:

- What changed and why.
- Any migrations, data refreshes, or config changes.
- Tests or checks that were run.
- Known limitations or follow-up work.

## Local Checks

Use the Make targets as the stable entrypoint:

```bash
make lint
make test
make format
```

If a target cannot run because dependencies are not installed yet, document that
in the pull request rather than silently skipping validation.
