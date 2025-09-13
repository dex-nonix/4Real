import {createApp, h} from 'vue'
import Tooltip from "primevue/tooltip";
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'

import NxApp from '@nonix/NxApp.vue'
import {createRouter} from '@nonix-router'
import NxLayoutManager from "@nonix-dynamic/manager/NxLayoutManager.js";
import NxPageManager from "@nonix-dynamic/manager/NxPageManager.js";
import NxDisplayWidgetManager from "@nonix-dynamic/manager/NxDisplayWidgetManager.js";
import NxEditWidgetManager from "@nonix-dynamic/manager/NxEditWidgetManager.js";
import NxDynamicWidgetManager from "@nonix-dynamic/widget/NxDynamicWidgetManager.js";
import NxWebSocketService from "@nonix-ws/services/NxWebSocketService.js";

import NotFound from "@/views/NotFound.vue";


const ensureCallback = callback => {
    if (Array.isArray(callback)) {
        const target = callback[0];
        callback = target[callback[1]].bind(target);
    }
    return callback;
};

const iterArray = (arr, callback) => {
    if (!arr) return;
    callback = ensureCallback(callback);
    for (const item of arr) {
        callback(item);
    }
};

const iterObject = (obj, callback) => {
    if (!obj) return;
    callback = ensureCallback(callback);
    for (const key in obj) {
        callback(key, obj[key]);
    }
};
const loadConfigObject = (app, config) => {
    iterArray(config.use, [app, "use"])
    iterObject(config.service, (key, value) => app.provide(key, value(app)));
    iterObject(config.layouts, (key, item) => NxLayoutManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.pages, (key, item) => NxPageManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.displayWidgets, (key, item) => NxDisplayWidgetManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.editWidgets, (key, item) => NxEditWidgetManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.dynamicWidgets, (key, item) => NxDynamicWidgetManager.registerWidget(key, item.component, item.defaultProps));
};

export const mountNxApp = (target, config = {}) => {
    const app = createApp({render: () => h(NxApp)});
    config.routes.push({path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: {layout: 'alt'}});
    app.use(createRouter(config.routes));
    app.use(PrimeVue);
    app.use(ToastService);
    app.directive('tooltip', Tooltip);
    app.websocketManager = new NxWebSocketService();
    app.provide('websocket-manager', app.websocketManager);

    loadConfigObject(app, config);
    iterObject(config.packages, (packageConfig) => loadConfigObject(app, packageConfig));
    app.mount(target);
};
