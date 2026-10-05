# Tailwind CSS stack pack

Written for: Tailwind 4

- [ ] **Tokens**: Colours, fonts, and spacing come from the project's theme tokens (`@theme` variables / configured scale); no arbitrary hex values like `text-[#a1b2c3]`.
- [ ] **Inline style**: Only for values computed at runtime; static styling uses utilities.
- [ ] **Responsive**: Mobile-first; larger breakpoints added with `sm:`/`md:`/`lg:` prefixes, not by overriding desktop styles down.
- [ ] **States**: `hover:`, `focus-visible:`, `disabled:` variants present on interactive elements.
- [ ] **Dark mode**: Uses the project's dark-mode mechanism consistently, not a mix of strategies.
- [ ] **Class conflicts**: No contradictory utilities on one element (`p-2 p-4`); conditional classes merge predictably.
- [ ] **Custom CSS**: Kept to the project's stylesheet location; `@apply` only for repeated, named patterns.
