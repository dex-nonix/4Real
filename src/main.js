import { createApp, h } from 'vue'
import App from '@/App.vue'
import router from '@/router'

import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'

// API services (configure base URL from env)
import { API_BASE_URL } from '@/config.js'
import CrudService from '@/services/CrudService.js'

const app = createApp({ render: () => h(App) })
app.use(router)
app.use(PrimeVue)

// Provide a simple $api getter using CrudService factory
app.config.globalProperties.$api = {
  crud: (entity) => new CrudService({ baseURL: API_BASE_URL, entity })
}

app.mount('#app')

