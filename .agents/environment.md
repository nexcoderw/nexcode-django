# Environment and secrets

- Keep application secrets in the untracked `.env` file, or inject them through the deployment secret store. The existing server-managed `.env.production` must remain private and follow the same rules.
- Never hard-code signing keys, API credentials, access tokens, passwords, private keys, or credential-bearing URLs in source code, templates, JavaScript, Docker images, documentation, fixtures, or logs. Browser-delivered configuration is public even when it originates in `.env`.
- Keep `.env.example` synchronized with the variable names used by the application and private environment files. Each variable must have an immediately preceding comment explaining its purpose, required conditions, and safe configuration guidance. Leave every assignment empty; never copy actual values.
- Add or rename an environment variable in its consumer and `.env.example` together. Preserve existing private values; do not print private files or interpolate secrets into shell commands or tool output.
- Read secrets through environment configuration without embedded fallback credentials. Fail startup with variable names only when required secrets are missing. Require Cloudinary credentials only when that integration is enabled.
- Keep debug disabled in production. Configure explicit allowed hosts, trusted HTTPS origins, secure cookies, and HTTPS redirects for the deployment. Do not weaken production settings to make local commands pass.
- Ignore `.env` and all `.env.*` files in Git and Docker contexts, except the value-free `.env.example`. Never stage a private environment file. Restrict private file permissions to their owner and grant deployment access only where required.
- If an actual secret has been exposed, arrange revocation and rotation with its owner. Removing it from the latest file does not remove it from history. Do not rewrite Git history or rotate production credentials without authorization.
- CI-only disposable secrets may be generated at runtime; do not store production credentials in workflow definitions. Use the CI secret store for deployment credentials.
- Do not run security checks, tests, or scanners unless the user explicitly requests execution. Provide commands and state that they have not been run.
