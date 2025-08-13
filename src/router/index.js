import { createRouter, createWebHistory } from 'vue-router'
import CrudPage from '@/views/CrudPage.vue'

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
  { path: '/chat', name: 'chat', component: Chat, meta: { layout: 'master' } },
  ...CrudPage.createRoutes('albums', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('tracks', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('styles', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('rhyme-techniques', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('artists', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('personas', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('internal-tools', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('persona-tool-access', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('mcp-servers', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('persona-mcp-servers', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('chat-sessions', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('chat-messages', { displayMode: 'inline' }, { layout: 'master' }),
  ...CrudPage.createRoutes('tool-invocation-logs', { displayMode: 'inline' }, { layout: 'master' }),
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: { layout: 'alt' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

