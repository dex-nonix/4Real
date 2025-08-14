import DynamicPage from "@/pages/DynamicPage.vue";
import CrudPage from "@/pages/CrudPage.vue";

export const ROUTE_TYPES = {
    dynamic: function (definition) {
        return DynamicPage.createRoute(definition.path, definition.page, definition.meta);
    },
    crud: function (definition) {
        return CrudPage.createRoutes(definition.entity, definition.options, definition.meta);
    },
}