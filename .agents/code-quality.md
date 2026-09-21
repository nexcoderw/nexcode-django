# Code quality and comments

## Readable implementation

- Write small, focused functions with descriptive names, explicit dependencies, and straightforward control flow. Prefer the simplest implementation that meets the requirement.
- Follow the surrounding style without copying known defects. Use four-space Python indentation, explicit imports, and standard-library, third-party, then local import groups.
- Avoid wildcard imports, dead code, speculative abstractions, duplicated business logic, and unrelated formatting changes.
- Add useful type hints at new service boundaries or where types clarify behavior. Do not introduce a typing framework solely for simple annotations.
- Handle expected failures explicitly, provide useful user-facing errors, and log actionable context without credentials or personal data. Broad exception handling must have a documented boundary and purpose.

## Comments and documentation

- Add concise comments for non-obvious decisions, business constraints, performance tradeoffs, and security-sensitive behavior.
- Explain why a decision exists; do not narrate obvious assignments or add comments merely to fill space.
- Add docstrings to reusable functions or classes whose contract, side effects, or failure modes are not clear from their names and signatures.
- Keep comments accurate when changing behavior. Remove stale comments and commented-out code.
- Make TODOs actionable, with a reason and a follow-up reference when one exists.
- Update related configuration examples and documentation when a change alters setup or operation.

## Django and frontend correctness

- Validate user input with Django forms or explicit server-side validation. Enforce authorization and publication visibility in queries, including detail routes.
- Preserve CSRF protection and template escaping. Sanitize permitted rich text; never mark arbitrary user input safe or inject it into HTML strings.
- Pass structured data to JavaScript using safe serialization such as `json_script`; avoid interpolating template values directly into executable JavaScript.
- Keep secrets in environment variables. Document variable names and harmless examples in `.env.example` without copying real values.
- Use transactions for related database writes that must succeed together, and database constraints for invariants that must survive concurrent requests.
- Use semantic HTML, accessible form labels, keyboard operation, visible focus, and layouts that handle mobile screens, empty data, and long content.
- Keep dependencies minimal. Explain the need for new packages and check compatibility with the project's declared runtime before adding them.

## Verification

- For behavioral changes, add or update focused tests covering the changed contract and meaningful failure cases. Django checks alone are not behavior tests.
- Use the project's Python environment. In a development environment with `DJANGO_DB=sqlite` and `USE_CLOUDINARY_MEDIA=False`, run `python manage.py check` and the relevant `python manage.py test home` tests. Set `DJANGO_ENV=development` explicitly if the shell otherwise uses production settings.
- For model changes, run `python manage.py makemigrations --check --dry-run` after generating migrations, and verify migrations against a disposable database. Never migrate a shared or production database as a routine check.
- For production settings or deployment changes, run `python manage.py check --deploy` under representative production settings with non-secret test values. Validate affected shell scripts or container configuration as appropriate.
- For template, CSS, or JavaScript changes, inspect the affected pages at desktop and mobile sizes; check interactions, keyboard access, and browser errors.
- For documentation-only changes, inspect links, paths, command examples, and `git diff --check`; application tests are unnecessary unless behavior also changes.
- Report exactly which checks ran and their results. Disclose unavailable checks and existing failures; never imply an unrun check passed.
