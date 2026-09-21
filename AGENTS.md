# NEXCODE project instructions

These instructions apply throughout this repository. Before changing files, read the following rules in order and follow the relevant requirements throughout the task:

1. [Git workflow](.agents/git.md) — file-specific staging and commit commands, preservation of user changes, and no pushing.
2. [Project structure](.agents/structure.md) — directory ownership and placement conventions.
3. [Code quality](.agents/code-quality.md) — readable code, useful comments, correctness, and verification.
4. [Performance](.agents/performance.md) — efficient Django queries, lightweight pages, and measured results.
5. [SEO](.agents/seo.md) — content, metadata, discoverability, and indexing.

## Working agreement

- Inspect the current files and Git state before editing. Make focused changes that satisfy the task and preserve unrelated work.
- Follow the existing Django architecture. Treat performance, accessibility, and search discoverability as part of implementation quality.
- These rules guide future changes; they do not authorize an unsolicited refactor, deployment, or production data change.
- Keep these instructions and linked rules synchronized when project conventions change. Read any more specific `AGENTS.md` that applies to the files being changed.
- At completion, explain the change and verification results, then provide the exact per-file `git add` and `git commit -m "Message"` commands required by `.agents/git.md`. Generate commands by default; execute staging or commits only when explicitly requested. Never run `git push` or publish commits through another tool.
