## Master Layout (Left Nav + Content + Right Tools)

### Purpose
- **Primary app shell** providing three regions: left navigation, center content, right tools.
- **Renders the top bar/header**, which is populated entirely by the Page (data + custom UI).
- **Mobile-first** with PrimeVue components: collapsible left navigation and right slideout panel.

### Responsibilities
- Hosts the application chrome: top bar (with burger and tools buttons), left `Sidebar` with `PanelMenu`, main content area with `<router-view>`, and right `Sidebar` for tools.
- Controls open/close state for left and right sidebars.
- Provides a composable or event bus the views can use to toggle sidebars.

### Non-Responsibilities
- Does not invent header content. It only renders what the Page provides (data/slots).

### Regions
- **Top Bar (Header)**: Contains burger (left), page header area (center), and tools button (right). The page header area is populated from shared state and Teleport targets.
- **Left**: Navigation (collapsible, supports nested items).
- **Center**: Content area (renders `<router-view />`). Views render a `Page` which provides header state/slots.
- **Right**: Tools (slideout panel for filters, inspectors, or contextual tools).

### Header Region
- The layout owns the visual header container and renders:
  - Back button (if `back` in header state). Click invokes `onBack` if provided; otherwise emits a global back event.
  - Title (from header state `title`).
  - Actions (PrimeVue `Menu` from `actions` model).
  - Tools toggle (if `showRightToggle` in header state). Opens right `Sidebar`.
- The header has two Teleport targets for custom UI from Page:
  - `#page-header-left` (left zone)
  - `#page-header-right` (right zone)
- Precedence rules:
  - If a Teleport target receives content, it overrides the default data-driven content for that zone.
  - If all of `title`, `back`, and `actions` are absent and no Teleport content exists, the page header area collapses, leaving only the shell controls (burger/tools) visible.

### PrimeVue and PrimeFlex
- Left/Right panels: PrimeVue `Sidebar`.
- Left navigation: PrimeVue `PanelMenu` for nested items.
- Top bar/header: PrimeVue `Button`, `Menu` (for actions), and a flex container.
- Utilities: PrimeFlex (`flex`, `align-items-center`, `justify-content-between`, `gap-2`, `hidden md:block`, `block md:hidden`, `p-2 md:p-3`).

### Behavior and Responsiveness
- **Mobile-first**: both sidebars closed by default. The burger opens the left nav; a tools button opens the right panel.
- **Desktop**: left nav can be "pinned" open (keep `Sidebar` visible or simulate with a permanent column). Right tools remains toggleable.
- Support optional auto-pin on desktop via a media query check; keep logic simple and local to the layout.

### Sidebar Data Model (Left Nav)
- Use a simple array of items compatible with PrimeVue `PanelMenu`:
```
const leftNavItems = [
  {
    label: 'Music',
    icon: 'pi pi-music',
    items: [
      { label: 'Artists', icon: 'pi pi-user', to: { name: 'artists' } },
      { label: 'Albums', icon: 'pi pi-list', to: { name: 'albums' } },
      { label: 'Tracks', icon: 'pi pi-play', to: { name: 'tracks' } },
      { label: 'Chat', icon: 'pi pi-comments', to: { name: 'chat' } }
    ]
  },
  {
    label: 'AI',
    icon: 'pi pi-brain',
    items: [
      { label: 'Providers', to: { name: 'providers' } },
      { label: 'Model Mappings', to: { name: 'model-mappings' } }
    ]
  }
]
```

### Composables / APIs
- **App shell controls**: expose a lightweight composable the views can import to request toggles without coupling to the layout:
```
// src/layouts/composables/useAppShell.js
export function useAppShell() {
  // under the hood this talks to a small emitter or a store
  return {
    toggleLeft: () => {/* emit 'layout:toggle-left' */},
    toggleRight: () => {/* emit 'layout:toggle-right' */},
    openLeft: () => {/* ... */},
    closeLeft: () => {/* ... */},
    openRight: () => {/* ... */},
    closeRight: () => {/* ... */}
  }
}
```
- **Page header state**: provide a shared header store the layout reads and the Page writes to:
```
// src/layouts/master/usePageHeader.js
export function usePageHeader() {
  // state shape the layout consumes
  // { title?: string, back?: boolean, actions?: MenuItem[], showRightToggle?: boolean, onBack?: Function }
  return {
    setHeader: (state) => {/* merge and notify */},
    resetHeader: () => {/* clear to defaults */}
  }
}
```
- The `Page` component sets this header state via props or directly via `setHeader`. Teleport slots from Page render into `#page-header-left` and `#page-header-right`.

### Suggested File Structure (No God Files)
```
src/layouts/
  master/
    MasterLayout.vue          # Shell: top bar, left & right sidebars, content slot
    LeftNavSidebar.vue        # Wrapper around Sidebar + PanelMenu
    RightToolsSidebar.vue     # Wrapper around Sidebar (right position)
    TopBar.vue                # Burger + app title + tools button
    NavItems.js               # Left nav configuration (PanelMenu model)
    useAppShell.js            # Composable for toggling sidebars from views
    usePageHeader.js          # Shared header state between Page and layout
    index.js                  # Barrel export
```

### Integration with Page Component
- The layout renders the center content (`<router-view />`). Views render a `Page` which sets header state and optionally teleports custom header UI.
- The top bar includes burger (toggles left) and tools button (toggles right). Showing the tools button can be controlled by the Page via `showRightToggle` in header state.

### Alignment With BIG-PICTURE.md
- **PrimeVue-first**: `Sidebar`, `PanelMenu`, `Button`, optional `Toolbar`.
- **No overengineering**: small, focused components; no god files.
- **Mobile-first**: collapsible sidebars with clear toggles; desktop pinning optional.
- **Separation of concerns**: layout handles frame/side panels; page handles header/actions; views orchestrate both.

