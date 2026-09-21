# Public website content and SEO review

> Historical report: the design restoration reinstates the page templates and animations from `c8e2578`, including their earlier visible copy. Shared SEO metadata, sitemap/robots endpoints, and backend publication rules remain. The layout, content, accessibility, and performance findings below describe the superseded redesign, not the restored pages. No tests or browser checks were run for the restoration; verification is reserved for the user.

## Scope and content sources

Reviewed all 19 public page types: home, about, services, six service details, work list/detail, team list/detail, articles list/detail, training list/detail, contact, and feedback.

Company facts were checked against the supplied [NEXCODE LinkedIn profile](https://www.linkedin.com/company/nexcode-africa/about/), available through its [public regional listing](https://rw.linkedin.com/company/nexcode-africa). The copy now uses 2019 as the founding year, identifies Norrsken House Kigali, and explains custom work and existing systems. New service descriptions explain scope and next steps in original language. Unsupported client counts, stock biographies, placeholder prices, unlimited-service promises, repeated sales paragraphs and nonworking controls were removed.

Database-managed articles, project descriptions, team records and training records were not rewritten. Their presentation and metadata now use the published content safely; no live data was changed.

## What changed

| Area | Result |
| --- | --- |
| Homepage | Clear service proposition, selected projects and practical buying questions. |
| About | Company background, ways of working, and links to real team and project records. |
| Services | Distinct service content with deliverables, process and enquiry guidance; one shared detail layout. |
| Projects and team | Working detail links, optional images, published work only, and no invented credentials. |
| Articles | Published and released articles only, readable dates in initial HTML, safe rich text, and Article structured data. |
| Training | Actual listed sessions with dates, prices and status; honest empty states and working enquiry links. |
| Forms | Visible labels and validation errors, retained invalid entries, contextual enquiry subjects and clear confirmation messages. |
| Shared layout | Unique titles and descriptions, trusted canonical URLs, Open Graph, social cards, Organization structured data and English language declaration. |
| Discovery | Sitemap, robots endpoint, pagination links and separate canonicals for subsequent list pages. |
| Assets and navigation | Deferred lightweight navigation, keyboard focus handling, native FAQs, optional image handling and no blocking preloader. |

The SEO approach follows the [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide). Sitemap generation uses [Django's sitemap framework](https://docs.djangoproject.com/en/6.0/ref/contrib/sitemaps/). Rich text uses the pinned [nh3 sanitizer](https://nh3.readthedocs.io/en/latest/) to preserve supported formatting without executable HTML.

## Verification

- 15 Django regression tests passed, including all page metadata, publication boundaries, pagination, sitemap destinations, invalid external links, forms, JSON-LD escaping and rich-text sanitization.
- Browser checks passed for 19 page types at 1440px and 390px widths: 38 viewport checks with no horizontal overflow, broken images or JavaScript exceptions.
- Checked navigation opening and closing, Escape behavior, native FAQ expansion, service enquiry prefilling and navigation without JavaScript.
- Inspected screenshots of home, about, a service detail and contact. Browser fixtures used a disposable SQLite database. External fonts were blocked during these checks for deterministic rendering; this does not measure production font delivery.
- Django development and production deployment checks completed with the existing `ckeditor.W001` warning about the bundled legacy editor. Editor replacement is separate from public rich-text sanitization.
- Template lint, JavaScript syntax and Git whitespace checks passed. No schema migration was needed.

## Performance evidence

Comparison used the prior Git version and the updated code against the same disposable SQLite dataset of 12 published client projects. Queries were captured using Django's test client, with five warm requests after one warm-up for each route.

| Measure | Previous | Updated |
| --- | ---: | ---: |
| Homepage database queries | 11 | 3 |
| Portfolio database queries | 27 | 4 |
| Locally loaded JavaScript source bytes | 792,094 | 1,554 |

The script comparison excludes the previously loaded external Bootstrap bundle and counts uncompressed source bytes, not network transfer size. Query regression coverage confirms the portfolio query count does not grow for each additional card within a page.

Warm response timings varied during concurrent checks: the baseline sample medians were 16.54 ms for home and 37.74 ms for portfolio; updated sample medians ranged from 9.82–21.56 ms and 18.60–43.81 ms respectively. These local samples do not establish production latency improvements. Real-user Core Web Vitals and search ranking changes have not been measured.

## Deployment and editorial follow-up

Follow [the deployment guide](NEXCODE_SERVER_DEPLOYMENT.md). Install the updated requirements and collect static assets as usual. Set `SITE_URL=https://nexcode.africa` and `SEARCH_ENGINE_INDEXING=True` on the public production site; keep indexing disabled on previews. Check the live sitemap and canonical URLs after deployment, then submit the sitemap using the existing Search Console property.

Service copy lives in `home/content.py`; metadata defaults live in `home/seo.py`. Existing rich content should be reviewed after deployment because embedded frames, executable markup and arbitrary inline styles are deliberately removed by the sanitizer. Existing database content still needs editorial review by its owners; no client outcomes, qualifications or training guarantees have been invented.

No staging, commits, pushes, live database changes or deployment were performed.
