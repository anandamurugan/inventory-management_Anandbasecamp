# Migration notes

## Shell structure

Before:

```html
<div class="app">
  <header class="top-nav">...logo, nav links, language switcher, profile...</header>
  <FilterBar />            <!-- optional global bar -->
  <main class="main-content"><router-view /></main>
</div>
```

After:

```html
<div class="app">
  <AppSidebar :items="navItems" :brand="t('nav.companyName')" :subtitle="t('nav.subtitle')">
    <template #footer>
      <LanguageSwitcher />
      <ProfileMenu ... />
    </template>
  </AppSidebar>
  <div class="main-area">
    <FilterBar />
    <main class="main-content"><router-view /></main>
  </div>
  <!-- modals stay here, unchanged -->
</div>
```

```css
.main-area { margin-left: var(--sidebar-w); min-height: 100vh; transition: margin-left var(--transition); }
.main-content { max-width: var(--content-max); margin: 0 auto; padding: var(--space-8); }
@media (max-width: 767px) {
  .main-area { margin-left: 0; padding-top: 56px; } /* room for the mobile top bar */
  .main-content { padding: var(--space-4); }
}
```

Delete `.top-nav`, `.nav-container`, `.nav-tabs` and related CSS once nothing references them (grep first).

## Building nav items

Derive them from what already exists (the old links or the router) so routes and label keys do not drift:

```js
const navItems = computed(() => [
  { to: '/', label: t('nav.overview'), icon: 'home' },
  { to: '/inventory', label: t('nav.inventory'), icon: 'box' },
  // ...one entry per old nav link
])
```

Icons available in `AppSidebar.vue`: home, box, cart, wallet, trend, refresh, chart, dot (fallback). Add a path to its `ICONS` map for anything else.

## Gotchas

- Hard-coded labels in the old nav (not routed through `t()`): add a key to every locale file.
- Existing `position: sticky; top: 70px` offsets under the old header (filter bars, table headers) must change to `top: 0` or a token, because the header is gone.
- Components that used `100vw` or assumed full width may overflow beside the sidebar; use `100%`.
- Modals and overlays should sit above the sidebar (z-index higher than the sidebar's 100 and drawer backdrop's 90).
- The footer slot is narrow (about 200px expanded, 40px collapsed). Dropdown menus opening from it should open upward or to the right and must not be clipped by `overflow: hidden`.

## Footer slot: make the existing widgets sidebar-aware

The slot passes `collapsed` (`<template #footer="{ collapsed }">`). Existing header widgets (language switcher, profile menu) were built for a top bar, so expect to edit them:

- Add a `compact` prop (icon or avatar only) and pass `:compact="collapsed"`.
- Make them full width in the sidebar.
- Their dropdowns must open **upward** (`bottom: 100%`) or to the right, not down, or they fall off-screen. Remove any large `min-width` that was tuned for the top bar.

## Props to pass

`<AppSidebar>` takes `theme` (`light` or `dark`) and translated `nav-label`, `open-label`, `collapse-label`, `expand-label` strings. Add matching keys to every locale file; do not leave the English defaults in a localized app.

## Spacing sweep caveats

Snapping to the 4px scale rounds odd values (10px to 12px, 14px to 16px), which slightly changes density. Review the diff on dense tables and compact controls. A sweep that only touches padding, margin, gap and radius does not unify colors; handle one-off hex colors as a separate, explicit pass or report them as left alone. Also delete any global rule that only the old header used (for example a bare `.subtitle`) so it cannot leak onto unrelated elements.

## Active link state

The template highlights with `router-link-exact-active`. If the app has nested routes (`/orders/123` under Orders), switch to `router-link-active` for those items, except the root `/` item, which must stay exact.
