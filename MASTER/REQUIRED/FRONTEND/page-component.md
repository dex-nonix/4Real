## Page Component (PrimeVue-first, Mobile-first)

### Purpose
- **Single, reusable page container** the view uses directly. No route meta.
- **Controls page chrome**: optional header with back button, title, and actions; collapses for mobile.
- **Header auto-hides** when there is no title/back/actions/toolbar content to provide a full-bleed canvas.

### Responsibilities
- **Header rendering** (if needed): back button, title, actions, and optional tools toggle.
- **Mobile-first actions**: actions collapse into a kebab menu on small screens.
- **Emit-only toggles** to interact with the layout’s side panels; page does not manage layout state.

### Non-Responsibilities
- Does not render side navigations or right tools pane.
- Does not know about routing meta. All control is in the view.

### Component API
- **Props**
  - **title?: string**: Page title. If omitted and no other header content is present, header is hidden.
  - **back?: boolean**: Show back button when true.
  - **actions?: MenuItem[]**: PrimeVue Menu model array for page actions.
  - **dense?: boolean**: Tighter header paddings.
  - **sticky?: boolean**: Makes header sticky at the top of the viewport.
  - **hideHeaderOnEmpty?: boolean = true**: Hides header when there’s no title/back/actions and no header slots.
  - **showRightToggle?: boolean**: Renders a right-side tools button that emits a toggle event.

- **Emits**
  - **back**: Fired when back button is clicked (the view decides to `$router.back()` or anything else).
  - **toggle-left**: Intent to open/close left navigation (layout decides behavior).
  - **toggle-right**: Intent to open/close right tools panel (layout decides behavior).

- **Slots**
  - **default**: Main page content.
  - **header-left**: Custom content injected to the left side of the header (e.g., breadcrumbs). Renders alongside back/title.
  - **header-right**: Custom content injected to the right side of the header (e.g., extra buttons). Renders alongside actions.
  - **toolbar**: Full override of the header content region. When provided, replaces back/title/actions with your own layout.

### Rendering Rules
- Header is rendered when at least one is present: `title`, `back`, `actions`, `header-left` slot, `header-right` slot, or `toolbar` slot.
- When none exist and `hideHeaderOnEmpty` is true, no header is rendered and content is full-bleed.
- On small screens:
  - Actions collapse behind a kebab `Menu` button using PrimeVue `Menu` with the supplied model.
  - Optional left and right toggles are available via icon buttons that emit `toggle-left` and `toggle-right`.

### PrimeVue and PrimeFlex
- Uses PrimeVue `Button`, `Menu` and PrimeFlex utilities for layout/responsiveness.
- Suggested utility classes: `flex`, `justify-content-between`, `align-items-center`, `gap-2`, `p-2 md:p-3`, `hidden md:block`, `block md:hidden`, `sticky top-0`.

### Suggested File Structure
```
src/components/page/
  Page.vue                 # Orchestrates header + content; emits toggles
  PageHeader.vue           # Internal header renderer (uses PrimeFlex)
  PageBackButton.vue       # Small isolated back button
  PageActions.vue          # Responsive actions: inline on md+, kebab Menu on xs
  index.js                 # Barrel export
```

### Example Usage (in a View)
```vue
<script setup>
import { ref } from 'vue'
import Page from '@/components/page/Page.vue'

const actions = ref([
  { label: 'New', icon: 'pi pi-plus', command: () => {/* ... */} },
  { label: 'Export', icon: 'pi pi-upload', command: () => {/* ... */} }
])

function handleBack() {
  // this could be: router.back()
}

function toggleLeft() {
  // call into layout composable to open/close left nav
}

function toggleRight() {
  // call into layout composable to open/close right tools
}
</script>

<template>
  <Page
    title="Artists"
    :back="true"
    :actions="actions"
    :showRightToggle="true"
    @back="handleBack"
    @toggle-left="toggleLeft"
    @toggle-right="toggleRight"
  >
    <!-- Page content goes here -->
  </Page>
</template>
```

### Full-Screen Content Case
```vue
<Page>
  <!-- Full-bleed content (no header is rendered) -->
</Page>
```

### Integration With Layout
- The Page emits `toggle-left` and `toggle-right`. The view should forward those intents to the layout via a small composable (see Master Layout document) to open/close side panels.
- The Page does not import or depend on the layout, preserving isolation and reuse.

### Alignment With BIG-PICTURE.md
- **No god files**: header, back button, and actions are split into dedicated components under `src/components/page/`.
- **PrimeVue-first & mobile-first**: uses `Menu`, `Button`, PrimeFlex utilities; collapses actions on small screens.
- **View-driven**: no route meta; each view owns its header/back/actions via Page props and slots.


---

## Header Integration With Master Layout

### Core Idea
- The layout renders the visual header. The Page provides all header data and any custom header UI.
- Data is passed via a shared composable the layout reads and the Page writes: `usePageHeader`.
- Custom header UI is injected via Teleport into two named targets inside the layout header.

### Shared Header Store (composable)
```
// src/layouts/master/usePageHeader.js
// Shape consumed by the layout:
// { title?: string, back?: boolean, actions?: MenuItem[], showRightToggle?: boolean, onBack?: Function }
export function usePageHeader() {
  return {
    setHeader: (state) => {/* merge + notify listeners */},
    resetHeader: () => {/* clear to defaults */}
  }
}
```

### What the Page Provides
- Title, back flag, actions model, tools toggle flag, and optional `onBack` handler (via props or `setHeader`).
- Optional custom UI for header zones via Teleport:
  - Left zone target: `#page-header-left`
  - Right zone target: `#page-header-right`

### Precedence Rules
- If a Teleport target receives content, it overrides that zone’s data-driven defaults (title/back on the left; actions/tools on the right).
- If no header data and no Teleport content are provided, the header collapses (only shell controls like burger/tools may remain).

### Minimal Example (Page inside a View)
```vue
<script setup>
import { ref } from 'vue'
import Page from '@/components/page/Page.vue'
import { usePageHeader } from '@/layouts/master/usePageHeader'

const actions = ref([
  { label: 'New', icon: 'pi pi-plus', command: () => {} },
  { label: 'Export', icon: 'pi pi-upload', command: () => {} }
])

// Option 1: Provide via Page props (recommended)
// Option 2: Use setHeader(...) directly if you need imperative control
const { setHeader, resetHeader } = usePageHeader()
</script>

<template>
  <Page
    title="Artists"
    :back="true"
    :actions="actions"
    :showRightToggle="true"
    @toggle-left="$emit('toggle-left')"
    @toggle-right="$emit('toggle-right')"
  >
    <!-- Optional: override header zones -->
    <template #header-left>
      <Breadcrumb :model="[{label:'Music', to:{name:'home'}},{label:'Artists'}]" />
    </template>
    <template #header-right>
      <Button label="Sync" icon="pi pi-refresh" @click="sync()" />
    </template>

    <!-- Page content -->
  </Page>
</template>
```

### Notes
- The Page no longer renders its own header; it feeds the layout header.
- Use PrimeVue `Menu` model for `actions`; the layout will render them and collapse to a kebab on mobile.
- Use the `useAppShell` composable to open/close left/right sidebars in response to `toggle-left`/`toggle-right` emitted by Page.

