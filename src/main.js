import { createApp, h } from 'vue'
import App from '@/App.vue'
import router from '@/router'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'

// API services (configure base URL from env)
import { API_BASE_URL } from '@/config.js'

const app = createApp({ render: () => h(App) })
app.use(router)
app.use(PrimeVue)
app.use(ToastService)

// No global $api registry/factory used; services are imported where needed

app.mount('#app')

