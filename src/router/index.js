import { createRouter, createWebHistory } from 'vue-router'
import CrudPage from '@/pages/CrudPage.vue'
import DynamicPage from '@/pages/DynamicPage.vue'

const Home = () => import('../views/Home.vue')
const About = () => import('../views/About.vue')
const NotFound = () => import('../views/NotFound.vue')
const DynamicFormExample = () => import('../views/DynamicFormExample.vue')
const DynamicTableExample = () => import('../views/DynamicTableExample.vue')
const Chat = () => import('../views/Chat.vue')

const routes = [
  { path: '/', name: 'home', component: Home, meta: { layout: 'master' } },
  { path: '/about', name: 'about', component: About, meta: { layout: 'alt' } },
  { path: '/dynamic-form', name: 'dynamic-form', component: DynamicFormExample, meta: { layout: 'master' } },
  { path: '/dynamic-table', name: 'dynamic-table', component: DynamicTableExample, meta: { layout: 'master' } },
  DynamicPage.createRoute('/dashboard', 'dashboard'),
  { path: '/chat', name: 'chat', component: Chat, meta: { layout: 'master' } },
  ...CrudPage.createRoutes('albums', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('tracks', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('styles', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('rhyme-techniques', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('ai-providers', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('ai-model-mappings', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('ai-analysis-results', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('artists', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('personas', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('internal-tools', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('persona-tool-access', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('mcp-servers', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('persona-mcp-servers', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('chat-sessions', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('chat-messages', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('tool-invocation-logs', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('file-categories', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('files', { displayMode: 'inline' }),
  ...CrudPage.createRoutes('file-links', { displayMode: 'inline' }),
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: { layout: 'alt' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

