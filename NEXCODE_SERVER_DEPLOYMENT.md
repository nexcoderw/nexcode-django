# Nexcode Django Deployment

This adapts `SERVER_DEPLOYMENT_PLAYBOOK.md` to this Django repo and the production domain `nexcode.africa`.

## Deployment Targets

- Project name: `nexcode`
- Project Linux user: `nexcode`
- Repo URL: `https://github.com/nexcoderw/nexcode-django.git`
- Live app path: `/var/www/nexcode/api`
- Releases path: `/var/www/nexcode/releases/api`
- Shared env path: `/var/www/nexcode/shared/api/.env.production`
- Shared media path: `/var/www/nexcode/shared/media`
- PM2 config path: `/var/www/nexcode/shared/pm2/nexcode-api.ecosystem.config.cjs`
- Local app port: `8000`
- Public domains: `nexcode.africa`, `www.nexcode.africa`

## DNS

Point these `A` records to `164.68.111.25` before requesting HTTPS:

- `@ -> 164.68.111.25`
- `www -> 164.68.111.25`

Remove any broken `AAAA` records if IPv6 is not configured on the server.

## One-Time Server Setup

Install the Ubuntu packages the base playbook expects, plus Python runtime packages for Django:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git nginx build-essential curl unzip snapd openssh-server ufw \
  python3 python3-venv python3-pip python3-dev libpq-dev
```

Install Node.js LTS and PM2 using the base playbook, then create the project user and directory layout:

```bash
sudo adduser nexcode
sudo usermod -aG sudo nexcode

sudo mkdir -p /var/www/nexcode/releases/api
sudo mkdir -p /var/www/nexcode/shared/api
sudo mkdir -p /var/www/nexcode/shared/media
sudo mkdir -p /var/www/nexcode/shared/logs
sudo mkdir -p /var/www/nexcode/shared/pm2
sudo mkdir -p /var/www/nexcode/bin
sudo chown -R nexcode:nexcode /var/www/nexcode
```

## Production Env File

Create the server-side env file and keep it off Git:

```bash
sudo -u nexcode touch /var/www/nexcode/shared/api/.env.production
sudo chmod 600 /var/www/nexcode/shared/api/.env.production
```

Use `.env.example.production` as the production variable-name template and `.env.example.local` for local development. Both contain intentionally blank assignments. Fill the production values in the server-managed `.env.production` before startup. Django requires a private `SECRET_KEY` in every environment and rejects production debug mode. The deployment script links `.env.production` to `.env`; never commit either private file.

Use separate Neon branches for development and production. Copy each branch's pooled connection string from the Neon dashboard into that environment's private `DATABASE_URL`; pooled endpoint hostnames contain `-pooler`. Keep `sslmode=require` and any `channel_binding` option supplied by Neon in the URL.

Production configuration example (placeholders only):

```dotenv
DJANGO_ENV=production
DEBUG=False
SITE_URL=https://nexcode.africa
SEARCH_ENGINE_INDEXING=True
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=postgresql://USER:PASSWORD@ENDPOINT-pooler.REGION.aws.neon.tech/DBNAME?sslmode=require
DATABASE_CONN_MAX_AGE=30
ALLOWED_HOSTS=nexcode.africa,www.nexcode.africa
CSRF_TRUSTED_ORIGINS=https://nexcode.africa,https://www.nexcode.africa
CLOUDINARY_CLOUD_NAME=replace-me
CLOUDINARY_API_KEY=replace-me
CLOUDINARY_API_SECRET=replace-me
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
PORT=8000
```

## Search indexing and content

`SITE_URL` is the trusted HTTPS origin for canonical links, social metadata and sitemap entries. Keep `SEARCH_ENGINE_INDEXING=True` only on the public production site. Development and preview deployments must use `False`; their public pages send `noindex` and their sitemap is disabled. Protect private staging environments with authentication as well.

After deployment, verify `/robots.txt`, `/sitemap.xml`, and the rendered canonical URLs. The sitemap excludes draft or scheduled articles, unpublished projects, and the feedback form. Submit the sitemap through the site's existing Search Console property when ready.

Install the updated `requirements.txt` before restarting: public rich text now uses the pinned `nh3` sanitizer. Run static collection as usual to publish the restored original animation script. The shared layout loads the original stylesheets and animation libraries; the redesign override stylesheet is no longer used. No database migration is required for this change.

Company copy follows the supplied [NEXCODE LinkedIn profile](https://www.linkedin.com/company/nexcode-africa/about/). Service detail pages have been removed. Existing detail URLs permanently redirect to `/services/` and are excluded from the sitemap; service enquiry links open the contact form with the subject prefilled. Service content data lives in `home/content.py`; metadata defaults live in `home/seo.py`. Article, project, team and training records remain managed through Django admin. Review existing rich content after deployment: supported formatting is preserved, while executable HTML, embedded frames and arbitrary inline styles are removed.

## Copy Repo Deployment Files To The Server

Copy these files from this repo to the server paths required by the playbook:

- `deploy/bin/nexcode-api-deploy.sh` -> `/var/www/nexcode/bin/nexcode-api-deploy.sh`
- `deploy/bin/nexcode-prune-releases.sh` -> `/var/www/nexcode/bin/nexcode-prune-releases.sh`
- `deploy/pm2/nexcode-api.ecosystem.config.cjs` -> `/var/www/nexcode/shared/pm2/nexcode-api.ecosystem.config.cjs`
- `deploy/nginx/nexcode.africa.conf` -> `/etc/nginx/sites-available/nexcode.africa.conf`

Then make the scripts executable and enable the Nginx site:

```bash
sudo chmod +x /var/www/nexcode/bin/nexcode-api-deploy.sh
sudo chmod +x /var/www/nexcode/bin/nexcode-prune-releases.sh
sudo ln -s /etc/nginx/sites-available/nexcode.africa.conf /etc/nginx/sites-enabled/nexcode.africa.conf
sudo nginx -t
sudo systemctl reload nginx
```

## First Deploy

The PM2 process must run as the `nexcode` user:

```bash
sudo -iu nexcode
cd /var/www/nexcode/releases/api
git clone https://github.com/nexcoderw/nexcode-django.git first-clone-check
rm -rf first-clone-check
exit

sudo -iu nexcode /var/www/nexcode/bin/nexcode-api-deploy.sh main
sudo -iu nexcode pm2 status
curl -I http://127.0.0.1:8000/health/
```

If the local health check passes, issue HTTPS certificates:

```bash
sudo certbot --nginx -d nexcode.africa -d www.nexcode.africa
sudo certbot renew --dry-run
```

## GitHub Actions Deployment

This repo should deploy by SSH to the server and execute the exact commit SHA on the server. GitHub repository access remains HTTPS. Configure the GitHub `production` environment with:

- `DEPLOY_HOST`
- `DEPLOY_PORT`
- `DEPLOY_USER`
- `SSH_PRIVATE_KEY`
- `SSH_KNOWN_HOSTS`

`DEPLOY_USER` should normally be `nexcode`.

The deploy script clones the repository over HTTPS:

```text
https://github.com/nexcoderw/nexcode-django.git
```

The SSH key in GitHub Actions is only for logging into your server. It is not a GitHub deploy key and does not need to be added under GitHub repository SSH settings.

If the repository is private and HTTPS clone asks for credentials on the server, create `/home/nexcode/.netrc` with a GitHub fine-grained token instead of switching to SSH:

```text
machine github.com
login YOUR_GITHUB_USERNAME
password YOUR_GITHUB_TOKEN
```

## Post-Deploy Checks

Run these after each deploy:

```bash
sudo -iu nexcode pm2 status
ls -l /var/www/nexcode
curl -I http://127.0.0.1:8000/health/
curl -I https://nexcode.africa/health/
curl -I https://nexcode.africa/
```

## Important Security Note

The current repo contains a real-looking `.env.production` with production credentials. Treat those secrets as exposed:

1. Rotate the database password.
2. Rotate the Cloudinary credentials.
3. Generate a fresh Django `SECRET_KEY`.
4. Keep the real `.env.production` only on the server at `/var/www/nexcode/shared/api/.env.production`.
