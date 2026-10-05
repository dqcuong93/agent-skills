# Astro stack pack

Written for: Astro 6

- [ ] **Static by default**: Components ship no JS unless they need it; `client:*` only on islands that must hydrate.
- [ ] **Directive choice**: `client:visible` or `client:idle` for below-the-fold or non-urgent islands; `client:load` only for what must work immediately.
- [ ] **Island props**: Serialisable (no functions, class instances, or circular data).
- [ ] **Prerender vs SSR**: On prerendered routes, `Astro.cookies`, request headers, and per-request data are build-time only; code that depends on them belongs on an SSR route.
- [ ] **`set:html`**: Only with trusted or sanitised content.
- [ ] **Images**: Content images go through `astro:assets` (`<Image />`) with dimensions; files in `public/` are served unoptimised.
- [ ] **Env**: `PUBLIC_*` variables are exposed to the browser and fixed at build time; secrets never use that prefix.
- [ ] **Styles**: Component `<style>` stays scoped unless a global rule is intended and placed in a global stylesheet.
