# Project structure

NEXCODE is a Django application with server-rendered templates, plain CSS and JavaScript, Neon PostgreSQL for development and production, and PostgreSQL for CI. Preserve this architecture unless the task calls for a change.

## File ownership

| Path | Responsibility |
| --- | --- |
| `AGENTS.md` | Entry point that loads the project rules. |
| `.agents/` | Shared engineering and delivery rules. |
| `nexcode/` | Django settings, root URL configuration, ASGI and WSGI entry points. |
| `home/models.py` | Domain models and database constraints. |
| `home/views.py` | Request handling, response selection, and view context. |
| `home/forms.py` | Form definitions and input validation. |
| `home/urls.py` | Application routes and named URLs. |
| `home/migrations/` | Versioned schema and data migrations. |
| `home/tests.py` | Current application tests. Split into `home/tests/` only when needed; remove the conflicting module when converting. |
| `templates/layouts/` | Shared page shells. |
| `templates/inc/` | Reusable template fragments. |
| `templates/services/`, `templates/work/`, `templates/blogs/`, `templates/team/`, `templates/training/` | Feature-specific pages. |
| `static/css/`, `static/js/`, `static/img/`, `static/fonts/` | Authored static assets and existing third-party assets. |
| `staticfiles/` | Generated `collectstatic` output; do not hand-edit. |
| `media/` | Runtime uploads; do not treat as application source. |
| `deploy/` | Server deployment scripts, Nginx and PM2 configuration. |
| `docker/`, `Dockerfile`, `docker-compose.yml` | Container startup and runtime configuration. |
| `.github/workflows/` | CI and deployment automation. |
| `.env.example.local`, `.env.example.production`, `requirements.txt` | Local and production variable templates and pinned Python dependencies. |
| `NEXCODE_SERVER_DEPLOYMENT.md` | Server deployment instructions. |

## Placement rules

- Keep related changes within their feature and reuse existing layouts and fragments.
- Keep business rules out of templates and routing modules. Introduce focused service or query modules within `home/` only when actual complexity or reuse warrants them.
- Create another Django app only for a distinct domain with clear ownership; do not create empty architectural layers.
- Use named URLs and Django's URL reversing instead of hard-coded internal links.
- Use descriptive `snake_case` names for new Python modules and functions, and `PascalCase` for classes. Preserve existing public names unless updating their references is in scope.
- Add forward migrations for model changes. Never rewrite migrations already applied in shared environments.
- Edit first-party source assets, not minified vendor libraries or collected copies. Vendor upgrades must be deliberate and versioned.
- Keep `venv/`, local database artifacts, caches, and secrets out of new commits. Do not reorganize existing tracked artifacts without a task requiring it.
- Update this map when introducing or moving a major directory.
