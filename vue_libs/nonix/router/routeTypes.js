import NxDynamicPage from "@nonix-dynamic/page/NxDynamicPage.vue";
import NxCrudPage from "@nonix-crud/pages/NxCrudPage.vue";

export const NX_ROUTE_TYPES = {
    dynamic: function (definition) {
        return NxDynamicPage.createRoute(definition.path, definition.page, definition.meta);
    },
    crud: function (definition) {
        return NxCrudPage.createRoutes(definition.entity, definition.options, definition.meta);
    },
}