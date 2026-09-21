# Git workflow

These rules apply to every repository change, including documentation and these rules themselves.

## Required handoff

- After generating, editing, deleting, or renaming files, include copyable Git commands in the final response for every file changed by the task.
- Provide one explicit `git add` command followed by one `git commit -m "Message"` command per file. Describe that file's actual change in its commit message.
- Generate these commands for the user to run. Execute staging or commits only when the user explicitly requests it.
- Never run `git push`, any variant of it, or another tool or API that publishes local commits to a remote repository. Do not include push commands in the handoff.
- Run commands from the repository root. Paths must be repository-relative, with no absolute path, `./` prefix, or enclosing checkout directory.
- For `home/views.py`, use `home/views.py`, never `nexcode/home/views.py`. The real Django configuration package is also named `nexcode`: its settings path must remain `nexcode/settings.py`, never `settings.py` or `nexcode/nexcode/settings.py`.
- Specify the complete file path, including its directory. Root-level files use their filename. Never stage a whole directory, a wildcard, `git add .`, `git add -A`, or `git commit -a`.
- Use `--` before file paths and quote paths containing spaces or shell metacharacters. For a rename, explicitly stage both the old and new path in the same file's commit.

## Review and isolation

1. Inspect `git status --short`, the working diff, and the staged diff before editing or staging. Preserve all unrelated user changes.
2. Review the final diff and run the relevant checks before preparing commit commands.
3. Ensure the index contains only the intended file before each commit. Plain `git commit` includes everything staged, so never proceed with unrelated staged changes.
4. If the user has staged unrelated work, stop automatic staging and report it; do not unstage their work without authorization. For generated commands, state that they require an index with no unrelated staged changes.
5. If a file contains pre-existing user edits, do not suggest staging the entire file silently. Review individual hunks with `git add -p -- path/to/file`, or ask how the user wants those edits included when ownership cannot be determined.
6. Never discard work, rewrite history, amend commits, change branches, or delete branches as incidental cleanup. Require explicit authorization for those actions.
7. Do not commit secrets, local environment files, database contents, uploaded media, virtual environments, or generated static output. Existing tracked artifacts are not permission to change or remove them incidentally.

## Commit messages and examples

Use `<type>(<scope>): <specific change>` with an imperative summary. Typical types are `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, and `chore`. Avoid vague messages such as "updates" or "changes".

With no unrelated changes staged, a file-specific handoff looks like:

```sh
git add -- home/views.py
git commit -m "perf(home): prefetch portfolio images"

git add -- templates/layouts/app.html
git commit -m "feat(seo): add overridable page metadata"
```

Per-file commits may depend on earlier commits. List commands in dependency order and validate the complete change set; do not claim every intermediate commit passes checks unless verified. List both paths for a rename, and use an explicit `git add -- path/to/deleted-file` for a tracked deletion.

Finish by stating what changed, which checks ran, and any remaining limitations. Never report commands as executed when they were only generated.
