# Inertia stack pack

Written for: Inertia 2

- [ ] **Page names**: The page file path matches the name the backend passes to `render(...)`; a mismatch is a 404/blank page on a normal path (CRITICAL).
- [ ] **Forms**: `useForm()` for forms with several fields, validation errors, or file uploads; `router.post()` / `router.visit()` for simple actions with no user input. No manual `axios`/`fetch` to Inertia routes.
- [ ] **Button state**: Async actions re-enable controls in `onFinish`, not only `onSuccess`.
- [ ] **Uploads**: Requests with files are sent as `FormData` automatically; `forceFormData: true` is only for forcing multipart when no file is present. Do not flag its absence on file uploads.
- [ ] **Navigation**: `<Link>` or `router.visit()` for internal routes, not bare `<a href>`.
- [ ] **Partial reloads**: `only: [...]` when one section of a page refreshes; `preserveScroll`/`preserveState` where losing them hurts the user (filters, long lists).
- [ ] **Props**: Serialisable and minimal; no ORM objects, secrets, or data the page does not render.
- [ ] **Shared data**: Added through middleware only when every page needs it.
- [ ] **CSRF**: Inertia's CSRF headers are left intact.
