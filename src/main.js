import { createApp, h } from 'vue'
import App from '@/App.vue'
import router from '@/router'

import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'

createApp({ render: () => h(App) })
  .use(router)
  .use(PrimeVue)
  .mount('#app')

