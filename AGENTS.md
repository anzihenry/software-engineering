# Repository instructions

## Coding standards

- Before creating, modifying, or reviewing source code, use `skills/04-implementation-and-self-test/language-coding-standards/SKILL.md`.
- Always read its `references/common.md` and only the language references matching the files in scope.
- Treat committed formatter, linter, compiler, build, and test configuration as the executable project standard.
- Do not silently upgrade a language/toolchain, add a production dependency, weaken a check, or rewrite unrelated code.
- Run the project-defined formatting, static analysis/type checking, build, and relevant tests after code changes; report anything not run.

## Playbook maintenance

- Keep SKILL descriptions discriminating and instructions focused on decisions that improve execution.
- Update workflow and `skills/README.md` routing whenever a SKILL is added, removed, or changes responsibility.

## GitHub operations

- Use the GitHub CLI (`gh`) as the preferred interface for pull requests, issues, Actions, releases, repository settings, and other GitHub API operations.
- Use `git` for local commits, branches, fetches, pulls, and pushes; these Git data operations are not replaced by `gh`.
- If `gh` is unavailable or unauthenticated, stop the GitHub API operation and request installation or authentication. Do not silently fall back to a connector, browser automation, direct API calls, or the GitHub web UI unless the user explicitly authorizes that fallback.

## Repository checks

- Install development tools with `python3 -m pip install --requirement requirements-dev.txt`.
- Run `ruff check scripts tests skills/05-integration-validation/github-actions-bootstrap/scripts`, `ruff format --check scripts tests skills/05-integration-validation/github-actions-bootstrap/scripts`, `python3 -m unittest discover --start-directory tests`, and `python3 scripts/check_repository.py` after changing repository content or validation code.
