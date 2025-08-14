import {createApp, h} from 'vue'
import NxApp from '@nonix/NxApp.vue'
import {createRouter} from '@nonix/router'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'


export function mountNxApp(target, config={}){
    const app = createApp({render: () => h(NxApp)});
    app.use(createRouter(config.routes));
    app.use(PrimeVue);
    app.use(ToastService);
    Object.keys(config.service ?? {}).forEach(key => {
        app.provide(key, config.service[key]());
    });
    (config.use ?? []).forEach(item => {
        app.use(item);
    });
    app.mount(target);
}
