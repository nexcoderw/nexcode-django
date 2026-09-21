# SEO and discoverability

Apply these rules to new or changed public pages. They are engineering requirements for improvement, not a claim that the current site already implements them or a guarantee of ranking.

## Page content and metadata

- Render meaningful public content and links in Django's initial HTML response.
- Give each indexable page a descriptive title and useful, page-specific meta description. Provide overridable metadata blocks in `templates/layouts/app.html` with sensible defaults when implementing shared metadata.
- Use one clear primary heading with a logical heading hierarchy, descriptive internal links, and helpful original content. Avoid keyword stuffing.
- Set the document language to the actual content language, such as `en` for English. Use meaningful image alternatives and empty alt text for purely decorative images.
- Add accurate Open Graph and social-card metadata when social sharing is in scope. Use absolute public image and page URLs.

These content and discovery practices follow Google's [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide).

## URLs and indexing

- Use stable, descriptive slugs and named routes. When changing an established public URL, preserve it with a permanent redirect where a replacement exists.
- Provide one absolute HTTPS canonical URL per indexable page. Keep it consistent with the preferred hostname, redirects, and sitemap. Use trusted site configuration rather than arbitrary request input.
- Keep paginated pages independently discoverable; do not automatically canonicalize every page to the first page. Canonicals should represent equivalent content, following Google's [canonicalization guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).
- Maintain a sitemap of public, published canonical pages when implementing or extending sitemap support. Exclude drafts, private pages, broken URLs, and redirects; use truthful modification dates.
- Maintain appropriate robots directives. Treat `robots.txt` as crawler guidance, never access control. Use authentication for private content and `noindex` where indexing must be suppressed; a blocked crawler cannot read a page's `noindex` directive.
- Ensure preview and staging environments are protected from indexing without accidentally applying their restrictions to production.
- Return correct status codes: real missing pages return 404, permanently removed pages may return 410, and unavailable services return appropriate errors. Avoid soft 404 pages returning 200.
- Apply publication filters to list pages, detail views, related content, and sitemap entries consistently.

## Structured data and verification

- Add structured data only when it accurately describes visible content and fits the page, for example an organization, article, or breadcrumb trail. Never invent reviews, ratings, addresses, or business claims.
- Serialize JSON-LD safely and validate it with an appropriate structured-data validator when changed.
- Inspect rendered HTML for titles, descriptions, canonicals, language, headings, links, status codes, and indexing directives on affected routes. Check detail pages, empty content, and pagination when relevant.
- Test URL redirects and publication restrictions when changing routing or visibility. Verify sitemap entries resolve to their intended public pages.
- Apply the [performance rules](performance.md) alongside SEO work. Record unresolved issues without claiming measured improvements from documentation alone.
