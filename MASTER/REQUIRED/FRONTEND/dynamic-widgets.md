## Dynamic Widgets – Manager, Registry, and Renderers

A unified, dynamic widget system for non-form content (view extensions, inline panels, summaries). Mirrors DynamicForm/DynamicTable patterns.

### Goals
- Declarative widget lists in service configs: `view.before` and `view.after`.
- Same conditional semantics as forms (`check` returns boolean/object/array/null).
- Extensible via a registry + manager; no changes to core CRUD components.
- Responsive by default with PrimeFlex; full-width rows by default, overridable per item.

---

## Files

- `src/widgets/DynamicWidgetManager.js`
  - Subclass of `BaseWidgetManager`; seeded with `DYNAMIC_WIDGETS`
  - Use `getWidget(type, userProps)` from the base to resolve components and merge `defaultProps`
  - Implements `getDefaultWidget()` returning `{ component: 'div', props: { class: 'text-sm', innerHTML: 'Unknown widget' } }`
- `src/widgets/dynamic-widgets.js`
  - Registry mapping `type` → `{ component, defaultProps }`
- `src/components/widgets/DynamicWidget.vue`
  - Renders a single widget (by `type` or direct component)
- `src/components/widgets/DynamicWidgetList.vue`
  - Renders an array of items with `setup/check/props` support and responsive layout
  - Computes items asynchronously and renders the resolved list

---

## Service Config – Usage (generic)

Add a `view` section to any service config:

```js
view: {
  before: [ /* Dynamic widget items */ ],
  after: [
    { type: 'text_block', props: { class: 'text-sm', text: 'Helpful info...' } },
    {
      type: 'inline_crud',
      props: (ctx) => ({ entity: 'related-entity', refField: 'parent_id', refId: ctx.entityId, displayMode: 'inline' }),
      check: (ctx) => ctx.mode === 'view'
    }
  ]
}
```

`CrudPage.vue` renders in order:
- All `view.before` widgets
- `CrudManager`
- All `view.after` widgets

CrudManager remains untouched and generic.

---

## Dynamic Widget Item Schema

- `id?` (optional string): stable identifier for reference
- `type` (string) OR `component` (Vue component)
- `props?` (object | (ctx) => object) – props can be computed from context
- `setup?` (ctx) => boolean | object | array | null | Promise – optional pre-step per item
- `check?` (ctx) => boolean | object | array | null – conditional rendering step

Context `ctx` (single object) passed to `setup`/`check`/`props`:
```
{ service, mode, entityId, entity, entitySingular, entityPlural, current, extra }
```
Where:
- `current`: the current entity data object used by the page (same object shown in view/edit)
- `extra`: optional bag for page-level or caller-provided context

Evaluation order & semantics:
1) Resolve context
   - The list accepts a single `context` prop which can be:
     - An object → used as-is
     - A function (sync or async) → called to obtain the context object
2) Run `setup(ctx)` if provided
   - Returns are interpreted as:
     - `false` → skip item
     - `true`/`null`/`undefined` → keep item as-is
     - `object` → shallow-merge into the item (override fields), then continue
     - `array` → replace item with this array (expand), then continue per element
3) Run `check(ctx)`
   - Returns use the same interpretation as `setup(ctx)` (skip/keep/merge/expand)
4) Resolve final props
   - If `props` is a function: `props(ctx)` → object; else use object as-is

`check(ctx)` semantics:
- `false` → skip item
- `true`/`null`/`undefined` → render item as-is
- `object` → shallow-merge overrides into the item then render
- `array` → expand into multiple items in place

Example (array expansion; exact same style as forms):
```js
{
  type: 'text_block',
  props: { text: 'Basic info...' },
  check: (ctx) => {
    if (ctx.current?.status === 'active') {
      return [
        { type: 'text_block', props: { text: 'Advanced Option' } },
        { type: 'chart_widget', props: { source: 'tuning_metrics' } }
      ]
    }
    return true
  }
}
```

---

## Layout & Responsiveness

DynamicWidgetList renders items in a PrimeFlex grid:
- Default: each item full-width row (`col-12`)
- Customize with PrimeFlex classes in props (e.g., `class: 'col-12 md:col-6'`)
- List-level props: `gap`, `rowClass`, `wrap`, etc.

Per-item layout overrides:
- Supply PrimeFlex classes via `props.class` (e.g., `col-12 md:col-4 xl:col-3`).

---

## Registry (dynamic-widgets.js)

Currently provided built-ins in code:
- `persona_tools`: loads `PersonaToolsViewer.vue`
- `text_block`: render arbitrary text (simple `h('div', text)` implementation)
- `json_view`: pretty JSON view (stringifies objects/arrays)

Example registry entry:
```js
export const DYNAMIC_WIDGETS = {
  persona_tools: { component: () => import('@/components/widgets/PersonaToolsViewer.vue'), defaultProps: {} },
  text_block: { component: { props: { text: String }, render() { return h('div', this.text) } }, defaultProps: {} },
  json_view: { component: { props: { value: [Object, Array, String, null] }, render() { /* stringify */ } }, defaultProps: {} }
}
```

DynamicWidgetManager resolves by `type` and merges `defaultProps` with user `props`.

### Single Widget Rendering
- Use `<DynamicWidget widget="type-or-definition" :props="..." :context="ctx" />` to render one item anywhere.
- `widget` can be a string type (resolved via registry) or a full definition object (with `type/component`, `props`, `check`).

---

## Examples (generic)

### Inline Related CRUD (after)
```js
view: {
  after: [
    {
      type: 'inline_crud',
      props: (ctx) => ({ entity: 'attachments', refField: 'owner_id', refId: ctx.entityId, displayMode: 'inline' })
    }
  ]
}
```

### Stats + Chart Row (before)
```js
view: {
  before: [
    { type: 'stats_card', props: { label: 'Items', value: 42, icon: 'pi pi-database', class: 'col-12 md:col-3' } },
    { type: 'stats_card', props: { label: 'Active', value: 13, icon: 'pi pi-check', class: 'col-12 md:col-3' } },
    { type: 'chart_widget', props: { source: 'entity_trend' , class: 'col-12 md:col-6' } }
  ]
}
```

### Conditional Insert (form-style; array expansion)
```js
view: {
  after: [
    {
      type: 'text_block',
      props: { text: 'Overview' },
      check: (ctx) => ctx.current?.status === 'active'
        ? [
            { type: 'text_block', props: { text: 'Advanced Option' } },
            { type: 'json_view', props: { value: ctx.current?.settings } }
          ]
        : true
    }
  ]
}
```

---

## Notes
- Use the `dynamic-*` prefix consistently (DynamicWidgetManager, dynamic-widgets.js, DynamicWidget.vue, DynamicWidgetList.vue).
- The system is declarative and mirrors DynamicForm config patterns for minimal surprise.

### Explicit Check Semantics (inline)
For every item, evaluate `check(ctx)` and apply the result as follows:
- `false` → do not render this item
- `true` / `null` / `undefined` → render the item as-is
- `object` → shallow-merge the object into the item (override fields), then render
- `array` → replace this item with the returned array of items and process each using the same rules (array expansion)

Context `ctx` provided to `check` and `props` functions contains:
```
{ service, mode, entityId, entity, entitySingular, entityPlural, current, extra }
```
Where `current` is the current entity data shown on the page; `extra` is an optional bag for page-level context.

