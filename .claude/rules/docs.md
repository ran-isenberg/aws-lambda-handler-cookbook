---
paths:
  - "docs/**"
---

## Documentation

Docs are built with **Zensical** (MkDocs-Material lineage): `make docs` serves locally,
`make publish-docs` builds to `site/` (published to GitHub Pages by the main pipeline).

### Rules

- **Markdown lints via `make lint-docs`** (`markdownlint-cli --fix` against `.markdownlint.yaml`).
  Run it before committing docs. Repo conventions from that config:
    - Top-level heading is `##` (h2), not `#` — MD041 requires level 2; increment one level at a time.
    - Line length ≤ 380 (headings ≤ 80); tables are exempt.
    - Fenced code blocks need a language and blank lines around them; end files with a single newline.
- **Runnable examples:** the snippets under `docs/examples/` are real, importable Python that the
  handler/best-practice pages reference. Keep them working — they follow the same layering and
  Powertools conventions as `service/` (see `.claude/rules/service.md`), and tests may import them.
- **OpenAPI schema** lives at `docs/swagger/openapi.json`. It is generated, not hand-edited. After any
  API change run `make openapi`; `make compare-openapi` (part of `make pr`) fails the build if the
  committed schema drifted from what the code produces.
- Prose changes should stay in sync with code: if you change behavior, update the page that documents it.
