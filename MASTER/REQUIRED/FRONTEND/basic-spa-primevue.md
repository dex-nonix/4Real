## Basic SPA (Vue 3 + PrimeVue) — Minimal, Reusable, Routed

Goal: A minimal, working SPA baseline that proves the routing, reusable layouts, and a PrimeVue button — nothing fancy. Two routes (`/` and `/about`), each using a different layout. Also include a 404 route. This is the foundation before any widgets or CRUD.

### Stack
- **Vue 3** (Vite)
- **Vue Router**
- **PrimeVue** + **PrimeIcons** + **PrimeFlex** (Prime-first; no custom CSS)

### Folder Layout (root level)
```
4Real/
  ├─ index.html
  ├─ package.json
  ├─ vite.config.js
  └─ src/
     ├─ main.js
     ├─ App.vue
     ├─ router/
     │  └─ index.js
     ├─ layouts/
     │  ├─ MasterLayout.vue      # Used by Home
     │  └─ AltLayout.vue         # Used by About
     └─ views/
        ├─ Home.vue              # Route: /
        ├─ About.vue             # Route: /about
        └─ NotFound.vue          # Route: 404 catch-all
  ├─ backend/                    # Flask backend (unchanged)
  └─ .venv/                      # Python virtualenv (unchanged)
```

### Dependencies
```json
{
  "dependencies": {
    "vue": "^3.4.38",
    "vue-router": "^4.4.5",
    "primevue": "^3.52.0",
    "primeicons": "^6.0.1",
    "primeflex": "^3.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.2",
    "concurrently": "^9.0.0",
    "vite": "^5.4.2"
  }
}
```

### Setup (one-time)
```bash
# From repo root
cd /home/dex/Desktop/shadewalk/4Real
npm install
# Dev server proxies /api to http://localhost:5000 by default (see vite.config.js)
## Environment vars
# Dev: VITE_API_BASE_URL=/api
# Prod: VITE_API_BASE_URL=https://backend-host:5000/api
```

### Minimal Files — Content

index.html
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>4Real</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
  </html>
```

src/main.js
```js
import { createApp, h } from 'vue'
import App from './App.vue'
import router from './router'

// Prime (PrimeVue + PrimeFlex) minimal setup
import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'
// NOTE: PrimeVue components are imported locally in views to keep global minimal

import CrudService from '@/services/CrudService'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const app = createApp({ render: () => h(App) })
app.use(router)
app.use(PrimeVue)
// Provide CRUD factory (base URL comes from environment automatically)
app.config.globalProperties.$api = { crud: (entity) => new CrudService({ entity }) }
app.mount('#app')
```

src/App.vue
```vue
<template>
  <!-- Switch layouts by route meta -->
  <component :is="layout">
    <router-view />
  </component>
  
  <!-- Simple nav for demo -->
  <nav style="margin-top: 1rem;">
    <router-link to="/">Home</router-link>
    <span style="margin: 0 0.5rem;">|</span>
    <router-link to="/about">About</router-link>
  </nav>
  <hr />
  <small>Layout: {{ layoutName }}</small>
  
  <!-- The NotFound view also uses layouts via meta -->
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MasterLayout from './layouts/MasterLayout.vue'
import AltLayout from './layouts/AltLayout.vue'

const route = useRoute()
const layouts = { master: MasterLayout, alt: AltLayout }

const layoutName = computed(() => route.meta.layout || 'master')
const layout = computed(() => layouts[layoutName.value] || MasterLayout)
</script>
```

src/router/index.js
```js
import { createRouter, createWebHistory } from 'vue-router'

const Home = () => import('../views/Home.vue')
const About = () => import('../views/About.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { layout: 'master' },
  },
  {
    path: '/about',
    name: 'about',
    component: About,
    meta: { layout: 'alt' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
    meta: { layout: 'alt' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

src/layouts/MasterLayout.vue
```vue
<template>
  <div style="padding: 1rem; border: 2px solid #4caf50;">
    <header><h2>Master Layout</h2></header>
    <main>
      <slot />
    </main>
  </div>
  </template>
```

src/layouts/AltLayout.vue
```vue
<template>
  <div style="padding: 1rem; border: 2px dashed #1976d2;">
    <header><h2>Alt Layout</h2></header>
    <main>
      <slot />
    </main>
  </div>
  </template>
```

src/views/Home.vue
```vue
<template>
  <section>
    <h1>Hello World (Home)</h1>
    <p>This page uses the Master layout.</p>
    <Button label="PrimeVue Button" icon="pi pi-check" />
  </section>
  </template>

<script setup>
import Button from 'primevue/button'
</script>
```

src/views/About.vue
```vue
<template>
  <section>
    <h1>About</h1>
    <p>This page uses the Alt layout.</p>
  </section>
  </template>
```

src/views/NotFound.vue
```vue
<template>
  <section>
    <h1>404 — Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
  </section>
  </template>
```

vite.config.js (with API proxy)
```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
})
```

### npm Scripts
```json
{
  "scripts": {
    "dev": "concurrently -n api,ui -c blue,green \"npm:dev:api\" \"npm:dev:ui\"",
    "dev:api": "./.venv/bin/python backend/cli.py run --host 0.0.0.0 --port 5000 --debug",
    "dev:ui": "vite --host 0.0.0.0 --port 5173",
    "build": "vite build",
    "preview": "vite preview --host 0.0.0.0 --port 5174"
  }
}
```

### Acceptance Criteria
- App runs with `npm run dev` from repo root and starts both backend and frontend.
- Backend serves at http://localhost:5000
- Frontend serves at http://localhost:5173
- Visiting `/` renders Home view inside `MasterLayout` and shows a PrimeVue Button.
- Visiting `/about` renders About view inside `AltLayout`.
- Visiting any unknown path shows `NotFound` in a layout.
- Nav links switch routes without reload.
- Backend and frontend run concurrently via npm scripts.

### Notes
- Keep global PrimeVue config minimal. Import individual components locally until we add more widgets.
- Use PrimeFlex for layout/spacing; avoid custom CSS.
- Configure backend host via `VITE_API_BASE_URL` (dev: `/api`, prod: `https://host:port/api`).
- This doc defines only the baseline. Widgets/CRUD come later.
- npm-first project structure with UI at root level, backend in `backend/` subdirectory.
- Uses concurrently to run both servers from single npm command.


