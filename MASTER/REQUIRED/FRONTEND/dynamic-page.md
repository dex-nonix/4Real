## Dynamic Page – Config-Driven Pages with Dynamic Widgets

A generic page renderer powered by the DynamicWidget system. Use it for dashboards, detail pages, or any non-CRUD view. No core hacks; fully declarative via config.

### Goals
- Define pages entirely in config: header + a list of dynamic widgets
- One context object (or resolver function) drives all widgets
- Identical widget item semantics to forms: optional `setup(ctx)`, `check(ctx)`, `props(ctx)`
- Responsive by default using PrimeFlex (row/col classes)

---

## Files (building blocks)
- `src/components/widgets/DynamicWidgetList.vue` – renders a list of items with setup/check/props flow
- `src/components/widgets/DynamicWidget.vue` – renders a single item by `type` or `component`
- `src/widgets/DynamicWidgetManager.js` – subclass of `BaseWidgetManager`; seeded from `dynamic-widgets.js`
- `src/widgets/dynamic-widgets.js` – widget registry (`type` → `{ component, defaultProps }`)

---

## Dynamic Page Config

Shape:
```js
export const myPage = {
  header: {
    title: 'Dashboard',      // string or (ctx) => string
    back: false,             // optional
    actions: [               // optional header actions
      { label: 'Refresh', icon: 'pi pi-refresh', command: (ctx) => ctx.extra?.refresh?.() }
    ]
  },
  layout: {                  // optional list defaults
    rowClass: 'grid',
    gap: 'gap-3'
  },
  widgets: [ /* Dynamic widget items */ ],
  context: ({ route, inject }) => ({       // object or function (sync/async)
    // Example context: feel free to return anything your widgets need
    service: inject('dashboard-service'),
    mode: 'view',
    entityId: route.params?.id,
    extra: { refresh: () => inject('dashboard-service').refresh() }
  })
}
```

Context `ctx` available to all items:
```
{ service, mode, entityId, entity, entitySingular, entityPlural, current, extra }
```
- `current` is optional; fetch it in a widget’s `setup(ctx)` or within the widget if needed

---

## Manager Pattern (uniform)

- **Base class**: `src/widgets/BaseWidgetManager.js`
  - `getWidget(type, userProps)` merges registry `defaultProps` with `userProps`
  - `registerWidget(type, component, defaultProps)` to extend at runtime
  - Subclasses implement only `getDefaultWidget()`; no custom APIs
- **Subclasses**:
  - `DisplayWidgetManager.js` → seeds `DISPLAY_WIDGETS`, trivial `getDefaultWidget()`
  - `EditWidgetManager.js` → seeds `EDIT_WIDGETS`, trivial `getDefaultWidget()`
  - `DynamicWidgetManager.js` → seeds `DYNAMIC_WIDGETS`, trivial `getDefaultWidget()`
- **Registries** are pure maps (`type` → `{ component, defaultProps }`): `display-widgets.js`, `edit-widgets.js`, `dynamic-widgets.js`

This keeps all managers identical in structure and usage with zero special-case logic.

---

## Dynamic Widget Item Schema (recap)

- `id?` (optional string)
- `type` (string) OR `component` (Vue component)
- `props?` (object | (ctx) => object)
- `setup?` (ctx) => boolean | object | array | null | Promise
- `check?` (ctx) => boolean | object | array | null

Evaluation order per item:
1) Resolve `ctx` (object or call a resolver function; await if Promise)
2) Run `setup(ctx)` if provided
   - `false` → skip; `true/null/undefined` → keep; `object` → merge; `array` → expand
3) Run `check(ctx)` (same semantics)
4) Resolve final `props` (if function → `props(ctx)`)

Layout:
- PrimeFlex; default `col-12` per item; override via `props.class` (e.g., `col-12 md:col-6`)

---

## Examples

### 1) Simple Dashboard
```js
export const dashboardPage = {
  header: { title: 'Dashboard' },
  layout: { rowClass: 'grid', gap: 'gap-3' },
  context: () => ({ mode: 'view' }),
  widgets: [
    { type: 'stats_card', props: { label: 'Users', value: 1024, icon: 'pi pi-users', class: 'col-12 md:col-3' } },
    { type: 'stats_card', props: { label: 'Active', value: 128, icon: 'pi pi-check', class: 'col-12 md:col-3' } },
    { type: 'chart_widget', props: { source: 'usage_trend', class: 'col-12 md:col-6' } }
  ]
}
```

### 2) Detail Page With Inline Related CRUD
```js
export const detailPage = {
  header: { title: (ctx) => `Details #${ctx.entityId}` },
  context: ({ route, inject }) => ({
    service: inject('orders'),
    entityId: route.params?.id
  }),
  widgets: [
    {
      type: 'inline_crud',
      props: (ctx) => ({ entity: 'order-items', refField: 'order_id', refId: ctx.entityId, displayMode: 'inline', class: 'col-12' })
    },
    {
      type: 'json_view',
      setup: async (ctx) => {
        const res = await ctx.service.get(ctx.entityId)
        const body = res?.data
        const current = body?.data || body || null
        return { props: { value: current }, class: 'col-12 md:col-6' }
      },
      check: (ctx) => true
    }
  ]
}
```

### 3) Conditional Insert (Array Expansion)
```js
export const conditionalPage = {
  header: { title: 'Conditions' },
  widgets: [
    {
      type: 'text_block',
      props: { text: 'Overview', class: 'col-12' },
      check: (ctx) => ctx.current?.status === 'active'
        ? [
            { type: 'text_block', props: { text: 'Advanced Option', class: 'col-12 md:col-6' } },
            { type: 'json_view', props: { value: ctx.current?.settings, class: 'col-12 md:col-6' } }
          ]
        : true
    }
  ]
}
```

### 4) Persona Tools (purely as a page)
```js
export const personaToolsPage = {
  header: { title: (ctx) => `Persona ${ctx.entityId} Tools` },
  context: ({ route }) => ({ entityId: route.params?.id }),
  widgets: [
    { type: 'persona_tools', props: (ctx) => ({ personaId: ctx.entityId, class: 'col-12' }) }
  ]
}
```

---

## Integration Notes
- DynamicPage.vue (renderer) should:
  - Render a Page header using `config.header`
  - Render body via `<DynamicWidgetList :items="config.widgets" :context="config.context || {}" :rowClass="config.layout?.rowClass" :gap="config.layout?.gap" />`
- Keep pages declarative; any fetching can be done in widget `setup(ctx)` or inside widgets.

---

## DynamicPage.vue – Component API and Usage

### Location
- `src/views/DynamicPage.vue` (suggested)

### Props (minimal)
- `config` (object, required): the dynamic page config defined above

### Responsibilities
- Build a context object (or call the provided resolver function) and pass it to `DynamicWidgetList`
- Render the page header using your existing `Page`/header helpers (`usePageHeader`, etc.)

### Skeleton Implementation (example)
```vue
<template>
  <div class="dynamic-page">
    <!-- Header (use your existing Page/header system) -->
    <Page :title="resolvedTitle" :back="Boolean(config?.header?.back)" :actions="resolvedActions" />

    <!-- Body -->
    <DynamicWidgetList
      :items="config?.widgets || []"
      :context="contextResolver"
      :rowClass="config?.layout?.rowClass || 'grid'"
      :gap="config?.layout?.gap || 'gap-3'"
    />
  </div>
  </template>

<script>
import DynamicWidgetList from '@/components/widgets/DynamicWidgetList.vue'
import Page from '@/components/page/Page.vue' // or your header component
import { useRoute } from 'vue-router'
import { inject, computed } from 'vue'

export default {
  name: 'DynamicPage',
  components: { DynamicWidgetList, Page },
  props: { config: { type: Object, required: true } },
  setup(props) {
    const route = useRoute()
    const resolvedTitle = computed(() => typeof props.config?.header?.title === 'function'
      ? props.config.header.title({ route })
      : (props.config?.header?.title || ''))
    const resolvedActions = computed(() => props.config?.header?.actions || [])
    const contextResolver = () => (typeof props.config?.context === 'function'
      ? props.config.context({ route, inject })
      : (props.config?.context || {}))
    return { resolvedTitle, resolvedActions, contextResolver }
  }
}
</script>
```

### Router Usage (example)
```js
import DynamicPage from '@/views/DynamicPage.vue'
import { dashboardPage } from '@/configs/pages/dashboard.js'

export default createRouter({
  history: createWebHistory(),
  routes: [
    // meta.page accepts: string key | object config | function resolver (sync/async)
    { path: '/dashboard', component: DynamicPage, meta: { page: 'dashboard', layout: 'master' } },
    { path: '/inline', component: DynamicPage, meta: { page: dashboardPage, layout: 'master' } },
    { path: '/resolved', component: DynamicPage, meta: { page: ({ route, inject }) => ({ header: { title: 'Resolved' }, widgets: [] }), layout: 'master' } },
  ]
})
```

### As a View Wrapper
If you prefer to keep `CrudPage` and `DynamicPage` uniform, you can create a simple wrapper view per page:
```vue
<template>
  <DynamicPage :config="page" />
  </template>
<script>
import DynamicPage from '@/views/DynamicPage.vue'
import { dashboardPage as page } from '@/configs/pages/dashboard.js'
export default { components: { DynamicPage }, setup() { return { page } } }
</script>
```

This makes the component location and usage explicit and keeps all page content declarative via the `config` object.

---

## Static Helper: DynamicPage.createRoute

To declare routes succinctly, expose a static helper on `DynamicPage`:

### Signature
```js
DynamicPage.createRoute(path, page, meta = {})
// path: string
// page: string | object | function ({ route, inject }) => string | object | Promise
// meta: object (e.g., { layout: 'master' })
```

### Behavior
- Returns a single route record: `{ path, component: DynamicPage, meta: { page, ...meta } }`

### Examples
```js
const routes = [
  DynamicPage.createRoute('/dashboard', 'dashboard', { layout: 'master' }),
  DynamicPage.createRoute('/inline', { header: { title: 'Inline' }, widgets: [] }, { layout: 'master' }),
  DynamicPage.createRoute('/ops', ({ route, inject }) => ({ header: { title: 'Ops' }, widgets: [] }), { layout: 'master' })
]
```

---

## PageManager – DRY Registry (Subclass of BaseWidgetManager)

Purpose:
- Keep named, predefined dynamic pages in one place (only used when `meta.page` is a string)
- Mirror the BaseWidgetManager pattern so usage is consistent across the app

### Location
- `src/pages/PageManager.js`

### Design
Pages are “just widgets” with a different payload. Follow the exact subclass pattern from `BaseWidgetManager` with no extra methods.

```js
// src/pages/PageManager.js
import BaseWidgetManager from '@/widgets/BaseWidgetManager.js'

// Seed from a simple pages registry map (same shape as other registries)
// src/pages/pages.js
// export const PAGES = {
//   dashboard: { component: { header: { title: 'Dashboard' }, widgets: [] }, defaultProps: {} },
//   detail: { component: { header: { title: 'Detail' }, widgets: [] }, defaultProps: {} }
// }

import { PAGES } from '@/pages/pages.js'

class PageManager extends BaseWidgetManager {
  constructor() {
    // Directly seed the map; no adapters or transformations
    super(PAGES)
  }

  getDefaultWidget() {
    return { component: { header: { title: 'Page' }, widgets: [] }, props: {} }
  }
}

export default new PageManager()
```

### Usage
```js
import PageManager from '@/pages/PageManager.js'
// To read a page config: use the standard API
const { component: pageConfig } = PageManager.getWidget('dashboard')
```

### Resolution Rules in DynamicPage (final)
1) Read `meta.page`
2) If function → call with `{ route, inject }` (await if Promise) → baseConfig
3) Else if string → `PageManager.getWidget(name).component` → baseConfig
4) Else if object → baseConfig = meta.page
5) If `meta.pageOverride` is provided → deep-merge onto baseConfig (route wins)
6) Render header/layout; pass `baseConfig.context` (or `{}`) to `DynamicWidgetList`

This keeps routing flexible:
- Strings resolve via PageManager; objects and functions bypass it entirely.
- No double logic, no hidden behavior; one clear resolution path.

