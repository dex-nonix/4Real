import {createRouter as createVueRouter, createWebHistory} from 'vue-router'
import {NX_ROUTE_TYPES} from "./routeTypes.js";

function vueRouterBuilder(routes) {
    return routes.map(route => {
        const routeType = route.type;
        if (routeType) {
            const routeBuilder = NX_ROUTE_TYPES[route.type]
            if (routeBuilder) {
                return routeBuilder(route)
            }
            throw new Error(`Unknown route type: ${routeType}`)
        }
        return route;
    }).flat(); // Flatten the array since crud routes return an array of routes
}

export const createRouter = (routes) => {
    return createVueRouter({
        history: createWebHistory(),
        routes: vueRouterBuilder(routes)
    })
}
