# Design tokens

Add to the global stylesheet. Replace the color values with the app's existing palette where it has one; the defaults below are a neutral slate and blue scheme.

```css
:root {
  /* spacing: 4px scale */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;

  /* radius */
  --radius-sm: 6px; --radius-md: 8px; --radius-lg: 12px;

  /* color */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-border: #e2e8f0;
  --color-text: #0f172a;
  --color-text-muted: #64748b;
  --color-accent: #2563eb;
  --color-accent-soft: #eff6ff;
  --color-hover: #f1f5f9;

  /* elevation */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);

  /* layout (AppSidebar updates --sidebar-w when it collapses) */
  --sidebar-w-expanded: 248px;
  --sidebar-w: var(--sidebar-w-expanded);
  --sidebar-w-collapsed: 72px;
  --content-max: 1440px;
  --transition: 160ms ease;
}
```

## Type scale

| Use | Size | Weight |
| --- | --- | --- |
| Page title | 1.5rem | 700 |
| Section / card title | 1rem | 600 |
| Body | 0.875rem | 400 |
| Label / caption | 0.75rem | 500, muted |

Use letter-spacing of -0.02em on titles only.

## Page rhythm

- Content padding: `--space-8` desktop, `--space-4` on mobile.
- Gap between cards/sections: `--space-6`.
- Card padding: `--space-5`; card = surface, 1px border, `--radius-lg`, `--shadow-sm`.
- Table cell padding: `--space-3` vertical, `--space-4` horizontal.
