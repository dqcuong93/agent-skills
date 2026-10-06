# Astro stack pack (performance)

Written for: Astro 6

- [ ] **Static first**: A page or section that does not change per request is prerendered or rendered without client JavaScript.
- [ ] **Island directives**: A component that can wait uses `client:visible` or `client:idle`, not `client:load`; every island justifies the JavaScript it ships.
- [ ] **Islands count**: Many small islands on one page are weighed against one larger one; each island carries its own framework runtime cost on first use.
- [ ] **Images**: `<Image />` from the assets pipeline for content images, with `sizes` set to the rendered width; files in the public directory are not optimised by the build, so their source size must already match.
- [ ] **Scoped styles**: Component styles that matter for first paint are extracted with the critical CSS the project uses; check the build output rather than the dev server, which does not run that step.
