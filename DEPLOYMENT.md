# RNT Home Builder — GitHub → Vercel Deployment

Target repository: `rnt-home-builder`

## Hosted routes
- `/` — public staging homepage
- `/builder/home/` — visual homepage editor
- `/admin/` — Django admin
- `/api/v1/homepage/home/` — published homepage JSON
- `/api/v1/health/` — health endpoint

## Vercel setup
1. Import the GitHub repository into a new Vercel project named `rnt-home-builder`.
2. Keep the repository root as the Vercel project root; `manage.py` is at root.
3. Add Neon Postgres (or another Postgres provider) and connect it to the project so `DATABASE_URL` is provided.
4. Add secrets/config:
   - `DJANGO_SECRET_KEY`
   - `RNT_ADMIN_USERNAME`
   - `RNT_ADMIN_PASSWORD`
   - `RNT_ADMIN_EMAIL` (optional)
   - `RNT_STOREFRONT_ORIGIN=https://www.ruffntumblekids.com`
   - `DJANGO_ALLOWED_HOSTS=.vercel.app`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://*.vercel.app`
5. Deploy.

The Vercel build hook in `pyproject.toml` runs database migrations, seeds the initial homepage if the database is empty, and bootstraps the admin account from environment variables.

## Persistent media
For real image uploads, configure DigitalOcean Spaces using the `SPACES_*` environment variables. Do not depend on Vercel's ephemeral filesystem for uploaded media.
