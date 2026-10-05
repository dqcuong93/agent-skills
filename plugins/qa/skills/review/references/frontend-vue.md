# Vue stack pack

Written for: Vue 3

- [ ] **`<script setup>`** with the Composition API in new and changed components.
- [ ] **Typed props and emits**: `defineProps<{…}>()` / `defineEmits<{…}>()` (or runtime validators); props are never mutated.
- [ ] **List keys**: `v-for` has a unique, stable `:key` (an id, not the index); `v-if` is not on the same element as `v-for`.
- [ ] **Reactivity**: `ref` for primitives and replaced values, `reactive` only for objects kept by reference; no destructuring of reactive objects without `toRefs`.
- [ ] **`computed` over `watch`** for derived state; a `watch` exists only for side effects.
- [ ] **Cleanup**: Listeners, intervals, observers, and manual subscriptions are removed in `onUnmounted` (or the composable's scope).
- [ ] **`v-show` vs `v-if`**: `v-show` for frequent toggles, `v-if` for rarely shown content.
- [ ] **Async components**: `defineAsyncComponent()` for large or rarely rendered components.
- [ ] **Composables**: Return refs, not raw values, so callers stay reactive; one concern per composable.
