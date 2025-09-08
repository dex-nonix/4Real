// Registry of dynamic pages. Shape matches other registries:
// name -> { component: pageConfigObject, defaultProps: {} }

import MasterLayout from "@nonix-master-layout/MasterLayout.vue";
import AltLayout from "@/layouts/AltLayout.vue";
import AdvancedLayout from "@nonix-advanced-layout/AdvancedLayout.vue";

export const LAYOUTS = {
    master: {
        component: MasterLayout,
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


