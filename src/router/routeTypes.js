import DynamicPage from "@/core/page/DynamicPage.vue";
import CrudPage from "@/core/page/CrudPage.vue";

export const ROUTE_TYPES = {
    dynamic: function (definition) {
        return DynamicPage.createRoute(definition.path, definition.page, definition.meta);
    },
    crud: function (definition) {
        return CrudPage.createRoutes(definition.entity, definition.options, definition.meta);
    },
}