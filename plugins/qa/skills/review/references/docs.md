# Docs checklist

Tool-agnostic. Covers documentation and AI-tool configuration. Report only items the change affects. Site-generator rules are in the `docs-<stack>.md` packs; rules for one project (file names, update order, grep audits) are in the profile's `Docs checks`.

## 1. Contract accuracy

- [ ] **States the contract**: A feature or spec document gives the rules, the integration points, and what is live versus planned, so a reader can use the feature from it.
- [ ] **Matches shipped code**: Routes, endpoints, environment variables, ports, and commands in the text exist in the code or config. Grep when unsure; a reader who follows a dead route loses time and trust.
- [ ] **No stale labels**: A removed route, a wrong port, or a cancelled feature is not presented as live.
- [ ] **Renames followed**: A name, route, or field the diff removed or renamed is searched for in docs and comments (grep the old name); every hit is updated or deleted.

## 2. Links and navigation

- [ ] **Links resolve**: Relative links point to files and anchors that exist. No link points to a deleted file or to a temporary draft that will be removed.
- [ ] **Index and nav**: A new document has a row in the project's docs index, and in the site navigation when one exists.
- [ ] **Deleted pages**: When the change deletes or moves a page, links to it are retargeted to the page that now holds the content.

## 3. AI-tool configuration

- [ ] **One canonical context file**: The shared agent context (domain, commands, conventions) lives in one file. Files for other tools import it or point to it.
- [ ] **Adapters stay thin**: A tool-specific file holds only what is specific to that tool. A paragraph copied from the canonical file is a second source of truth that will drift.
- [ ] **No always-on domain copy**: Rules that load for every request do not restate the product or domain brief.
- [ ] **Skills list matches disk**: The list of skills or commands in the context file equals the ones that exist.
- [ ] **Read order consistent**: Docs that explain how the tools load context (which file first, what is ignored) match the files and ignore lists in the repo.

## 4. Figures

- [ ] **Figures follow the text**: A diagram, screenshot, or figure that the change makes false is updated or marked outdated. The text is the source of truth; the figure is a view of it.
