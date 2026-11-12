---
name: vue-saas-sidebar-redesign
description: Redesign a Vue 3 app's UI into a modern SaaS-style interface with a vertical left sidebar instead of a top nav bar, consistent spacing and a polished professional look. Use this skill whenever the user wants to restyle, modernize or "make it look like a SaaS dashboard", move navigation from the top to the side, add a collapsible sidebar, or clean up spacing and visual consistency in a Vue 3 application, even if they never say the word "sidebar".
---

# Vue 3 SaaS sidebar redesign

Turn a Vue 3 app that has a horizontal top nav into a SaaS-style shell: a left sidebar (collapsible to an icon rail, drawer on mobile), one spacing scale, and shared design tokens, without changing what the app does. The redesign is presentational; routes, data loading, API calls and component logic stay as they are.

## Workflow

1. **Inspect before editing.** Find the shell (usually `src/App.vue`), the router file, the global styles, and how labels are produced (i18n `t()` keys, or hard-coded strings). Note the existing colors, fonts and any rules in `CLAUDE.md` or similar (for example "no emojis", "scoped styles"). The redesign must respect them; the project's own conventions beat this skill's defaults.
2. **Check the project's delegation rules.** If the project says `.vue` work goes to a specific subagent, delegate to it (or follow its definition file if it is not registered).
3. **Establish tokens.** Add the CSS variables from `references/design-tokens.md` to the global stylesheet (or `:root` in the shell), seeded from the colors the app already uses so the look stays recognizably the same product. Tokens are what make spacing and color consistent: views should reference them instead of hand-picked values.
4. **Add the sidebar.** Copy `assets/AppSidebar.vue` to `src/components/`. Pass it the nav items built from the router/nav entries the app already has. Move the old top bar's extras (language switcher, profile menu, user area) into its `footer` slot, and adapt them for it (see `references/migration-notes.md`). Choose `theme="light"` or `"dark"` and pass translated aria-label props. Keep every existing route and label key; add new i18n keys to every locale file rather than leaving hard-coded strings.
5. **Rewire the shell.** In the shell component, remove the top-nav markup and its CSS, render `<AppSidebar>` beside a `.main-area` that is offset by `var(--sidebar-w)`, and keep global bars such as filters inside the content column. Details are in `references/migration-notes.md`.
6. **Normalize the views.** Sweep view and component styles for off-scale padding, margins, gaps, radii and one-off colors, and replace them with tokens. Do this mechanically, view by view; skip anything that would change layout logic. Do not add features.
7. **Verify.** Run the production build, then look at the real UI at desktop width, a narrow width (drawer behaviour), and with the sidebar collapsed. A passing build does not show that the layout works, so open the pages and check that the active item highlights, content is not hidden under the sidebar, and nothing scrolls horizontally.

## Rules that keep the result polished

- **One spacing scale.** Use 4px multiples only (the `--space-*` tokens). Mixed values like 0.625rem next to 0.7rem are what make UIs look unfinished.
- **Icons are inline SVG**, stroke-based, 20px, inheriting `currentColor`. Never use emoji and do not add an icon library unless the project already has one.
- **Active state is obvious but quiet:** tinted background plus accent text and icon; no heavy borders.
- **Collapsed rail keeps labels accessible:** set `title` and `aria-label` on each link so the icon-only state is usable.
- **Respect reduced motion** for the width and drawer transitions.
- **Do not hard-code widths in views** that assumed a full-width top layout; content should fill `.main-area`.
- **Preserve behaviour:** keep existing `router-link` targets, `$route` active logic and modal wiring. If something in the old header cannot be placed cleanly, say so rather than dropping it.

## Report back

Finish with: what changed (files), which tokens were introduced, what was verified and how, and anything left inconsistent that you chose not to touch.
