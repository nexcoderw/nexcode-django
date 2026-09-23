# Performance

Fast responses, lightweight pages, and responsive interactions are acceptance criteria for new work. Existing performance must be measured, not assumed.

## Targets and measurement

- Target LCP at or below 2.5 seconds, INP at or below 200 milliseconds, and CLS at or below 0.1 at the 75th percentile, evaluated separately for mobile and desktop. These follow the [Web Vitals guidance](https://web.dev/articles/vitals).
- Use browser profiling and Lighthouse for repeatable development comparisons. Lighthouse's loading audit does not measure real-user INP; distinguish lab results from field measurements.
- For performance-sensitive changes, record the affected route, dataset size, device/network conditions, query count, response timing, and relevant before/after measurements.
- Inspect both cold and warm behavior when caching matters. Define route-specific query and latency budgets from measurements rather than inventing a universal query limit.
- Do not claim a speed improvement or a passing target without evidence. If production field data is unavailable, state that limitation.

## Django and database

- Avoid N+1 queries. Use `select_related()` for appropriate single-valued relations and `prefetch_related()` for collections actually consumed by the page.
- Filter published, authorized data in the database. Paginate growing lists and use deterministic ordering rather than loading every row.
- Use `exists()`, `count()`, and database aggregation when appropriate; avoid evaluating a queryset only to answer a simpler question.
- Add indexes for demonstrated filtering or ordering needs and verify query plans. Account for index storage and write cost.
- Avoid redundant database or external-service calls in request handling. Cache shared public data only with explicit keys, expiration, and invalidation behavior.
- Never cache personalized responses as public content or let caches bypass authorization. Keep user identity, language, and other response-varying inputs in cache design.
- Use timeouts for external calls. Keep expensive processing out of requests when a measured need justifies background work; do not add infrastructure speculatively.

## Browser and assets

- Serve appropriately sized, compressed images with responsive variants where useful. Reserve image dimensions to prevent layout shifts.
- Process every uploaded raster image before storage. Use the shared `home.image_processing` policy to resize oversized uploads, encode them as WebP at quality 82, avoid enlarging smaller sources, and preserve transparency for cutouts. New image fields must use `ProcessedImageField`; any exception requires a documented product or compatibility reason and focused storage tests.
- Lazy-load below-the-fold images. Keep the main visible image discoverable and do not lazy-load the LCP image.
- Load only the scripts, styles, plugins, and font weights required by the page. Avoid introducing duplicate libraries.
- Defer non-critical scripts while preserving dependency order and existing initialization behavior. Verify changes against the project's jQuery and GSAP setup.
- Keep main-thread work small; avoid repeated synchronous layout reads and writes. Prefer transform and opacity animation, and respect reduced-motion preferences.
- Render useful content immediately. Do not make loaders or decorative animations block content or interaction.
- Preserve the existing static collection, compression, and cache setup. Use long-lived caching only for versioned assets; verify deployment behavior before changing cache headers.
- Add focused query-count or regression tests when they protect a measured optimization. Recheck affected behavior after optimizing.
