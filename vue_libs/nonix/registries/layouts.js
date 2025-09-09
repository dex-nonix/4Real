// Registry of dynamic pages. Shape matches other registries:
// name -> { component: pageConfigObject, defaultProps: {} }

import AdvancedLayout from "@nonix-advanced-layout/AdvancedLayout.vue";
import AltLayout from "@/layouts/AltLayout.vue";

export const LAYOUTS = {
    master: {
        component: AdvancedLayout,
        defaultProps: {}
    },
    advanced: {
        component: AdvancedLayout,
        defaultProps: {}
    },
    alt: {
        component: AltLayout,
        defaultProps: {}
    }
}


