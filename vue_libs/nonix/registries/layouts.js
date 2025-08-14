// Registry of dynamic pages. Shape matches other registries:
// name -> { component: pageConfigObject, defaultProps: {} }

import MasterLayout from "@nonix-master-layout/MasterLayout.vue";
import AltLayout from "@/layouts/AltLayout.vue";

export const LAYOUTS = {
  master: {
    component:MasterLayout,
    defaultProps: {} // not implemented yet!
  },
  alt: {
    component:AltLayout,
    defaultProps: {} // not implemented yet!
  }
}


