# Ruff 'n' Tumble Django Home Builder

## Vercel + GitHub deployment (recommended staging flow)

This package is prepared for the same **GitHub → Vercel Import Project** workflow used for the other projects. Vercel added zero-configuration Django support in 2026, so no `/api` shim or routing `vercel.json` is required.

### What the hosted staging project gives you

```text
/                  Customer-facing homepage staging preview
/builder/home/      Visual homepage editor (login required)
/admin/             Django admin
/api/v1/homepage/home/  Published JSON consumed by Next.js
/api/v1/health/     Health check
```

The root staging page reads the same homepage records as the builder. Draft changes appear in the builder preview immediately; clicking **Publish** updates the public staging homepage.

### Import flow

1. Create a GitHub repository named `rnt-home-builder`.
2. Push this folder to the repository's `main` branch.
3. In Vercel choose **Add New → Project → Import Git Repository** and select `rnt-home-builder`.
4. Vercel should detect **Django/Python** automatically. Do not add a custom build/output directory unless Vercel fails to detect the root `manage.py`.
5. Add a persistent Postgres database from **Vercel Marketplace/Storage**. **Neon Postgres** is recommended for staging because it supports serverless Postgres and database branching. The integration supplies `DATABASE_URL`.
6. Add the environment variables below.
7. Deploy. The Vercel build script runs migrations, seeds the RNT homepage when the database is empty, and creates/updates the admin user from environment variables.

### Required Vercel environment variables

Use **Secret** for passwords/keys.

```text
DJANGO_SECRET_KEY=<long random secret>
RNT_ADMIN_USERNAME=<your admin username>
RNT_ADMIN_PASSWORD=<strong password>
RNT_ADMIN_EMAIL=<optional email>
RNT_STOREFRONT_ORIGIN=https://www.ruffntumblekids.com
DJANGO_ALLOWED_HOSTS=.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.vercel.app
```

`DATABASE_URL` is normally added automatically by the Postgres integration.

For a later custom CMS domain, update:

```text
DJANGO_ALLOWED_HOSTS=.vercel.app,cms.ruffntumblekids.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.vercel.app,https://cms.ruffntumblekids.com
```

### Media uploads on Vercel

Do not rely on Vercel's temporary function filesystem for permanent homepage image uploads. Either keep using existing RNT DigitalOcean Spaces URLs, or configure the supplied `SPACES_*` environment variables so uploaded campaign images are stored persistently.


This package gives Ruff 'n' Tumble a **Django-powered homepage CMS** that can sit behind the existing storefront without replacing the ecommerce engine.

## Architecture this package assumes

The current public storefront is treated as the presentation/commerce layer. Django becomes a small CMS for homepage structure and campaign content only.

```text
RNT staff
   |
   v
Django Home Builder
- edit sections
- reorder
- hide/show
- schedule
- images
- CTAs
- product/category references
- preview
- publish
- revision snapshots
   |
   | JSON API
   v
Existing Ruff 'n' Tumble Next.js storefront
   |
   +-- existing product API / Odoo sync
   +-- existing inventory and pricing
   +-- existing cart/checkout
   +-- existing recommendations
   +-- existing Brevo/newsletter integration
```

This is deliberate. Do **not** duplicate product stock, price, variants, cart or order data in Django. Those remain in the current commerce stack.

## What the backend editor can do

- Reorder the homepage from top to bottom.
- Add, edit, duplicate and delete sections.
- Hide/show sections.
- Desktop/mobile visibility.
- Hero, category grid, product rail, editorial, split banner, video, story, social proof, newsletter and spacer blocks.
- Headings, copy, links and two CTAs.
- Desktop and mobile image URLs.
- Upload new desktop/mobile images.
- Reuse existing DigitalOcean Spaces image URLs.
- Choose product source: selected product refs/SKUs, category slug, new arrivals, recommendations.
- Schedule start and end times.
- Add/reorder section cards/slides/items.
- Live desktop/mobile preview in the editor.
- Publish only when ready.
- Published revision snapshots.

## Why Django is used this way

Do not convert the full Ruff 'n' Tumble shop into Django. The safer integration is:

1. Keep the current storefront and ecommerce APIs.
2. Run Django on a CMS host such as `cms.ruffntumblekids.com`.
3. The homepage in Next.js requests `GET /api/v1/homepage/home/`.
4. Django returns the published section schema.
5. Existing RNT product components use the schema's `productRefs`, `categoryKey`, and `source.type` to retrieve current product data.

This means changing a homepage campaign does not touch checkout or Odoo synchronization.

## Local setup

Python 3.12+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate              # macOS / Linux
# .venv\\Scripts\\activate             # Windows
pip install -r requirements.txt

cp .env.example .env
```

Export the variables from `.env`, then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_rnt_homepage
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/builder/home/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## API

Published homepage:

```text
GET /api/v1/homepage/home/
```

Draft preview:

```text
GET /api/v1/homepage/preview/<preview-token>/
```

Health check:

```text
GET /api/v1/health/
```

## Product integration rule

A product rail does **not** store product price or stock in Django.

Example payload:

```json
{
  "source": {
    "type": "selected_products",
    "categoryKey": "girls-dresses",
    "productRefs": ["FSHOE642-217BFITKXM", "PRODUCT-ID-123"],
    "limit": 8
  }
}
```

The current Next.js product service should resolve those references and render the existing ProductCard/ProductCarousel. This prevents stale price and stock in the CMS.

## Current homepage seed

Run:

```bash
python manage.py seed_rnt_homepage
```

It creates an editable starting structure for:

1. Hero
2. Back to School
3. Girls / Boys / Baby
4. Recommendations
5. Timotiwa
6. Our Story
7. Customer Love
8. Newsletter

It also preloads the known Back to School category paths:

```text
/category/girls-dresses
/category/footwear
/category/boys-matching-sets-sets
/category/boys-tops-shirts
```

Existing campaign image URLs can be retained without moving the files.

## DigitalOcean Spaces

Existing image URLs can simply be pasted into **Desktop image URL** or **Mobile image URL**.

For new CMS uploads, this project can also write to S3-compatible DigitalOcean Spaces if the `SPACES_*` environment variables are configured. If they are not configured, Django uses local media storage during development.

## Production database

On Vercel, use a persistent Postgres integration and `DATABASE_URL` (recommended). Split `DB_*` variables remain supported for non-Vercel hosting. If neither `DATABASE_URL` nor `DB_NAME` is set, the project uses SQLite for local development only.

## Next.js integration

See `nextjs-integration/`.

The important line on the storefront is:

```tsx
const payload = await getRntHomepage();
```

Then pass that payload into the renderer, while routing `product_rail` sections to the site's existing product carousel.

Do not replace the existing header/footer, cart, checkout or product API during the first deployment.

## Suggested production deployment

```text
www.ruffntumblekids.com  -> existing Next.js site
cms.ruffntumblekids.com  -> Django + Gunicorn + PostgreSQL
```

Set in the Next.js environment:

```text
RNT_HOME_CMS_URL=https://cms.ruffntumblekids.com
```

Set in Django:

```text
RNT_STOREFRONT_ORIGIN=https://www.ruffntumblekids.com
```

## Deployment sequence

1. Deploy Django CMS to staging.
2. Create a superuser and seed the current homepage.
3. Recreate current imagery and content in the editor.
4. Publish revision 1.
5. Connect the Next.js staging homepage to the Django API.
6. Map product rails to the current product/recommendation components.
7. Map newsletter to the current Brevo component.
8. Test desktop/mobile, category links, product prices, stock, cart and checkout.
9. Deploy the Next.js homepage integration.
10. Marketing can now rearrange the homepage without a frontend deployment.

## Important limitation

The public site does not expose enough information to safely hard-code the private product/Odoo API contract. This package therefore leaves that existing integration intact and only hands the storefront product references/category keys. Once the current frontend repository is available, the adapter in `nextjs-integration/page-example.tsx` can be replaced with the exact current product component and API calls.
