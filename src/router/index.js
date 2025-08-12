import { createRouter, createWebHistory } from 'vue-router'

const Home = () => import('../views/Home.vue')
const About = () => import('../views/About.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  { path: '/', name: 'home', component: Home, meta: { layout: 'master' } },
  { path: '/about', name: 'about', component: About, meta: { layout: 'alt' } },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: { layout: 'alt' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

