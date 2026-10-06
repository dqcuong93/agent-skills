# Frontend performance checklist

Framework-agnostic. Report only items the page or component can reach.

## 1. Measurement

- [ ] **A number first**: Bundle and chunk sizes (from the production build), and for pages Largest Contentful Paint, layout shift, and interaction delay (from Lighthouse or browser tools), are recorded before any change.
- [ ] **Real conditions**: Measurements use the production build and a throttled mobile profile when most traffic is mobile.

## 2. Loading

- [ ] **JavaScript shipped**: Code not needed for the first view is split out or loaded on demand; heavy dependencies are justified by what they cost in the build output.
- [ ] **Dependencies**: Unused packages are removed; two libraries doing the same job are not both shipped.
- [ ] **Critical path**: Fonts and above-the-fold styles do not block first paint longer than needed; anything below the fold waits.

## 3. Rendering

- [ ] **Long lists**: Lists of hundreds of items are paginated or virtualised.
- [ ] **Derived state**: Values computed from other state are cached or computed once, not recomputed on every render.
- [ ] **Layout shift**: Images, embeds, and late-loading content reserve their space with explicit dimensions.

## 4. Images and media

- [ ] **Format and size**: Modern formats; the source resolution matches the largest size it is rendered at, with separate mobile and desktop sources when they differ.
- [ ] **Loading**: Below-the-fold images load lazily; the first-view image is not lazy.

## 5. Network

- [ ] **Requests**: No duplicate request for the same data and no sequential chain that could run in parallel.
- [ ] **Caching**: Stable data is cached by the browser or an in-memory layer, with a stated lifetime.
