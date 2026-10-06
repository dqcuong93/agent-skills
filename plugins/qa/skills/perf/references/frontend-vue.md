# Vue stack pack (performance)

Written for: Vue 3

- [ ] **Computed over methods**: Derived values use `computed()`, not a method called in the template on every render.
- [ ] **Lists**: `v-for` has stable keys; very long lists are virtualised; `v-if` and `v-for` are not combined on the same element.
- [ ] **Async components**: Heavy or below-the-fold components use `defineAsyncComponent`.
- [ ] **Reactivity cost**: Large objects that are replaced as a whole use `shallowRef` or `markRaw`; deep watchers on big structures are avoided.
- [ ] **Watchers and effects**: Watchers are cleaned up and do not trigger network calls on every keystroke without a debounce.
