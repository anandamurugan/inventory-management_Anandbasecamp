<template>
  <!-- Mobile top bar: only visible below 768px -->
  <div class="mobile-bar">
    <button class="icon-btn" type="button" :aria-label="openLabel" @click="mobileOpen = true">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path :d="ICONS.menu" /></svg>
    </button>
    <span class="mobile-brand">{{ brand }}</span>
  </div>

  <div v-if="mobileOpen" class="backdrop" @click="mobileOpen = false"></div>

  <aside :class="['sidebar', `theme-${theme}`, { collapsed, 'mobile-open': mobileOpen }]" :aria-label="navLabel">
    <div class="sidebar-head">
      <div v-if="!collapsed" class="brand-text">
        <span class="brand">{{ brand }}</span>
        <span v-if="subtitle" class="subtitle">{{ subtitle }}</span>
      </div>
      <button class="icon-btn collapse-btn" type="button"
              :aria-label="collapsed ? expandLabel : collapseLabel"
              :aria-expanded="!collapsed" @click="toggleCollapsed">
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
          <path :d="collapsed ? ICONS.chevronRight : ICONS.chevronLeft" />
        </svg>
      </button>
    </div>

    <nav class="sidebar-nav">
      <router-link v-for="item in items" :key="item.to" :to="item.to" class="nav-link"
                   :title="collapsed ? item.label : null" :aria-label="item.label"
                   @click="mobileOpen = false">
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
          <path :d="ICONS[item.icon] || ICONS.dot" />
        </svg>
        <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" :collapsed="collapsed" />
    </div>
  </aside>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

// 24x24 viewBox, stroke-based paths (stroke is applied in CSS)
const ICONS = {
  home: 'M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6',
  box: 'M21 8l-9-5-9 5v8l9 5 9-5V8zM3 8l9 5 9-5M12 13v9',
  cart: 'M3 4h2l2.4 11h10.2L20 7H6M9 20a1 1 0 100-2 1 1 0 000 2zM17 20a1 1 0 100-2 1 1 0 000 2z',
  wallet: 'M3 7h16a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7zM3 7l12-3v3M16 14h2',
  trend: 'M3 17l6-6 4 4 8-8M15 7h6v6',
  refresh: 'M20 11a8 8 0 00-14.9-3M4 4v4h4M4 13a8 8 0 0014.9 3M20 20v-4h-4',
  chart: 'M4 20V10M10 20V4M16 20v-8M22 20H2',
  menu: 'M4 6h16M4 12h16M4 18h16',
  chevronLeft: 'M15 18l-6-6 6-6',
  chevronRight: 'M9 18l6-6-6-6',
  dot: 'M12 12m-2 0a2 2 0 104 0 2 2 0 10-4 0'
}

const STORAGE_KEY = 'sidebar-collapsed'

export default {
  name: 'AppSidebar',
  props: {
    // [{ to: '/path', label: 'Text', icon: 'home' }]
    items: { type: Array, required: true },
    brand: { type: String, default: '' },
    subtitle: { type: String, default: '' },
    // 'light' (white sidebar) or 'dark' (slate-900 sidebar on a light page)
    theme: { type: String, default: 'light', validator: (v) => ['light', 'dark'].includes(v) },
    // Pass translated strings from the app's i18n; English defaults keep the component usable alone
    navLabel: { type: String, default: 'Primary' },
    openLabel: { type: String, default: 'Open navigation' },
    collapseLabel: { type: String, default: 'Collapse sidebar' },
    expandLabel: { type: String, default: 'Expand sidebar' }
  },
  setup() {
    const route = useRoute()
    const mobileOpen = ref(false)

    // null = no saved choice, so the screen width decides; true/false = the user's own choice.
    // localStorage can throw (private mode, blocked storage); the sidebar must still work.
    const userPref = ref(null)
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved === '1') userPref.value = true
      else if (saved === '0') userPref.value = false
    } catch (e) { /* no saved choice */ }

    // Phones get the drawer; tablets and small laptops default to the icon rail
    const isMobile = ref(false)
    const isNarrow = ref(false)
    const mqMobile = window.matchMedia('(max-width: 767px)')
    const mqNarrow = window.matchMedia('(max-width: 1023px)')
    const syncMedia = () => { isMobile.value = mqMobile.matches; isNarrow.value = mqNarrow.matches }
    syncMedia()

    // The drawer always shows full labels, so the rail never applies on mobile
    const collapsed = computed(() => !isMobile.value && (userPref.value ?? isNarrow.value))

    // The content column reads --sidebar-w so it tracks the collapsed state
    const applyWidth = () => {
      document.documentElement.style.setProperty(
        '--sidebar-w',
        collapsed.value ? 'var(--sidebar-w-collapsed)' : 'var(--sidebar-w-expanded)'
      )
    }
    watch(collapsed, applyWidth, { immediate: true })

    const toggleCollapsed = () => {
      userPref.value = !collapsed.value
      try { localStorage.setItem(STORAGE_KEY, userPref.value ? '1' : '0') } catch (e) { /* ignore */ }
    }

    const onKey = (e) => { if (e.key === 'Escape') mobileOpen.value = false }
    onMounted(() => {
      window.addEventListener('keydown', onKey)
      mqMobile.addEventListener('change', syncMedia)
      mqNarrow.addEventListener('change', syncMedia)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('keydown', onKey)
      mqMobile.removeEventListener('change', syncMedia)
      mqNarrow.removeEventListener('change', syncMedia)
    })
    watch(() => route.path, () => { mobileOpen.value = false })

    return { ICONS, collapsed, mobileOpen, toggleCollapsed }
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed; inset: 0 auto 0 0; z-index: 100;
  width: var(--sidebar-w, 248px);
  display: flex; flex-direction: column;
  background: var(--color-surface, #fff);
  border-right: 1px solid var(--color-border, #e2e8f0);
  transition: width var(--transition, 160ms ease), transform var(--transition, 160ms ease);
}
.sidebar-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--space-2, 8px); height: 64px; padding: 0 var(--space-4, 16px);
  border-bottom: 1px solid var(--color-border, #e2e8f0);
}
.collapsed .sidebar-head { justify-content: center; padding: 0; }
.brand-text { display: flex; flex-direction: column; min-width: 0; line-height: 1.2; }
.brand { font-weight: 700; font-size: 1rem; color: var(--color-text, #0f172a); letter-spacing: -0.02em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.subtitle { font-size: 0.75rem; color: var(--color-text-muted, #64748b); }

.sidebar-nav { flex: 1; overflow-y: auto; padding: var(--space-4, 16px) var(--space-3, 12px); display: flex; flex-direction: column; gap: var(--space-1, 4px); }
.nav-link {
  display: flex; align-items: center; gap: var(--space-3, 12px);
  height: 40px; padding: 0 var(--space-3, 12px);
  border-radius: var(--radius-md, 8px);
  color: var(--color-text-muted, #64748b); text-decoration: none;
  font-size: 0.875rem; font-weight: 500;
  transition: background var(--transition, 160ms ease), color var(--transition, 160ms ease);
}
.collapsed .nav-link { justify-content: center; padding: 0; }
.nav-link:hover { background: var(--color-hover, #f1f5f9); color: var(--color-text, #0f172a); }
.nav-link.router-link-exact-active { background: var(--color-accent-soft, #eff6ff); color: var(--color-accent, #2563eb); }
.nav-link:focus-visible, .icon-btn:focus-visible { outline: 2px solid var(--color-accent, #2563eb); outline-offset: 2px; }
.nav-label { white-space: nowrap; }
svg { flex: none; fill: none; stroke: currentColor; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round; }

.sidebar-footer { padding: var(--space-3, 12px); border-top: 1px solid var(--color-border, #e2e8f0); display: flex; flex-direction: column; gap: var(--space-2, 8px); }
.collapsed .sidebar-footer { align-items: center; }

.icon-btn { display: grid; place-items: center; width: 32px; height: 32px; border: 0; border-radius: var(--radius-sm, 6px); background: transparent; color: var(--color-text-muted, #64748b); cursor: pointer; }
.icon-btn:hover { background: var(--color-hover, #f1f5f9); color: var(--color-text, #0f172a); }

/* Dark theme: re-point the tokens the sidebar uses, so the markup stays identical */
.theme-dark {
  --color-surface: #0f172a; --color-border: #1e293b; --color-text: #f1f5f9;
  --color-text-muted: #94a3b8; --color-hover: #1e293b; --color-accent-soft: #1e3a8a;
  --color-accent: #93c5fd;
  /* extra tokens the footer widgets use, re-pointed for readability on slate-900 */
  --color-border-strong: #334155; --color-danger: #f87171; --color-danger-soft: #3f1d24;
  --color-text-body: #e2e8f0;
}

.mobile-bar, .backdrop { display: none; }

@media (max-width: 767px) {
  .sidebar { width: 280px; transform: translateX(-100%); }
  .sidebar.mobile-open { transform: translateX(0); box-shadow: var(--shadow-md, 0 4px 12px rgba(15, 23, 42, 0.08)); }
  /* the rail only makes sense on desktop; in the drawer always show full labels */
  .collapse-btn { display: none; }
  .mobile-bar { display: flex; align-items: center; gap: var(--space-3, 12px); position: fixed; inset: 0 0 auto 0; z-index: 90; height: 56px; padding: 0 var(--space-4, 16px); background: var(--color-surface, #fff); border-bottom: 1px solid var(--color-border, #e2e8f0); }
  .mobile-brand { font-weight: 700; color: var(--color-text, #0f172a); }
  .backdrop { display: block; position: fixed; inset: 0; z-index: 95; background: rgba(15, 23, 42, 0.4); }
}
@media (prefers-reduced-motion: reduce) {
  .sidebar, .nav-link { transition: none; }
}
</style>
