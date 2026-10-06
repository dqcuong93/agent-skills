# MkDocs stack pack

Written for: MkDocs 1

- [ ] **Nav entry**: A new page appears in `nav` of the MkDocs config, unless the project's config turns omitted files into errors (then the strict build catches it).
- [ ] **Strict build**: `mkdocs build --strict` passes (or the project's wrapper for it); run it when the profile or the environment allows, otherwise say `not run`.
- [ ] **Relative links**: Links between pages use relative paths that resolve from the page's own location; anchors exist.
- [ ] **Assets**: Images and files a page references exist under the docs directory and are not excluded by the config.
- [ ] **Config in step**: A new top-level docs folder, a renamed page, or a moved file updates the config (nav, `exclude_docs`, plugins) in the same change.
