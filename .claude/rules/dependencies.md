## Dependencies

Two ecosystems: **Python** via `uv` (`pyproject.toml` + `uv.lock`) and **Node** via npm
(`package.json` + `package-lock.json`, used for `aws-cdk` and `markdownlint-cli`).

### Rules

- **Always update through `make update-deps`**, which does the whole set in the right order:
  `uv lock --upgrade` + `uv sync`, `pre-commit autoupdate`, fetch the latest `aws-cdk` from npm and
  pin it in `package.json`, then `npm install`. Don't hand-edit lockfiles.
- Never edit `uv.lock` or `package-lock.json` by hand — regenerate them.
- Keep `npm audit` at **0 vulnerabilities**. If an advisory needs a major bump (e.g. `markdownlint-cli`),
  bump the range in `package.json` and re-run `npm install`, then verify with `npm audit`.
- **Dependabot** already covers routine bumps: `github-actions` monthly, `pip` monthly (→ `main`),
  `npm` weekly (→ `develop`), all with a `chore` commit prefix. Don't duplicate those manually.
- GitHub Actions are a dependency too — pin them to SHAs. See `.claude/rules/github-actions.md`.
- After any dependency change, run the relevant suite (at least `make unit`) to confirm nothing broke,
  and commit the lockfile changes together with the manifest change.
