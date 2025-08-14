import {createApp, h} from 'vue'
import App from '@/App.vue'
import {createRouter} from 'src/core/router'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'

import {appConfig} from "@/appConfig.js";

const app = createApp({render: () => h(App)})
app.use(createRouter(appConfig.routes));
app.use(PrimeVue)
app.use(ToastService)

Object.keys(appConfig.service).forEach(key => {
    app.provide(key, appConfig.service[key]());
})

app.mount('#app')

