import {createApp, h} from 'vue'
import NxApp from '@nonix/NxApp.vue'
import {createRouter} from '@nonix/router'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'
import LayoutManager from "@nonix/widget-manager/LayoutManager.js";
import PageManager from "@nonix/widget-manager/PageManager.js";
import DisplayWidgetManager from "@nonix/widget-manager/DisplayWidgetManager.js";
import EditWidgetManager from "@nonix/widget-manager/EditWidgetManager.js";
import DynamicWidgetManager from "@nonix/widget-manager/DynamicWidgetManager.js";
import NotFound from "@/views/NotFound.vue";
import Tooltip from "primevue/tooltip";
import WebSocketManager from "@/services/WebSocketManager.js";


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
    iterObject(config.layouts, (key, item) => LayoutManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.pages, (key, item) => PageManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.displayWidgets, (key, item) => DisplayWidgetManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.editWidgets, (key, item) => EditWidgetManager.registerWidget(key, item.component, item.defaultProps));
    iterObject(config.dynamicWidgets, (key, item) => DynamicWidgetManager.registerWidget(key, item.component, item.defaultProps));
};

export const mountNxApp = (target, config = {}) => {
    const app = createApp({render: () => h(NxApp)});
    config.routes.push({path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: {layout: 'alt'}});
    app.use(createRouter(config.routes));
    app.use(PrimeVue);
    app.use(ToastService);
    app.directive('tooltip', Tooltip);
    app.websocketManager = new WebSocketManager();
    app.provide('websocket-manager', app.websocketManager);

    loadConfigObject(app, config);
    iterObject( config.packages, (packageConfig)=> loadConfigObject(app, packageConfig));
    app.mount(target);
};
