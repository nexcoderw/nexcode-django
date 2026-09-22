# Preserve the established design

- Keep the existing visual design exactly as supplied unless the user explicitly requests a design change. Content, SEO, security, routing, and performance work are not permission to redesign.
- Preserve CSS rules, stylesheet ordering, fonts and weights, colors, spacing, dimensions, responsive breakpoints, images, icons, and visual hierarchy.
- Preserve template wrappers, CSS classes, animation selectors, script order, dependencies, timing, scroll behavior, loaders, sliders, and hover interactions. Do not remove libraries or replace animated components incidentally.
- Change link destinations without changing their visible markup or styling. When removing a page, update incoming links, remove its sitemap entry, and preserve an appropriate redirect for existing public URLs.
- Do not restore deleted service detail pages as part of a design rollback. The services overview remains the public service page, and its service enquiries lead to the contact form.
- If a requested change cannot be made without a visible alteration, explain the specific conflict and obtain direction before changing the design.
- The restored design derives from `c8e2578`; preserve subsequent user-approved changes rather than blindly restoring entire files from that commit.
- Visual review belongs to the user. Do not launch browsers, take screenshots, or run automated checks unless explicitly requested. Never claim pixel-perfect verification when none was performed.
