import {reactive} from 'vue'

const shellState = reactive({
    leftOpen: false,      // mobile off-canvas visibility
    leftCollapsed: false, // desktop pinned collapse
    rightOpen: false,     // right sidebar visibility
    rightPinned: false    // right sidebar pinned state
})

const shell = {
    state: shellState,
    toggleLeft: () => {
        if (typeof window !== 'undefined' && window.innerWidth >= 768) {
            shellState.leftCollapsed = !shellState.leftCollapsed
        } else {
            shellState.leftOpen = !shellState.leftOpen
        }
    },
    toggleRight: () => shellState.rightOpen = !shellState.rightOpen,
    openLeft: () => shellState.leftOpen = true,
    closeLeft: () => shellState.leftOpen = false,
    openRight: () => shellState.rightOpen = true,
    closeRight: () => shellState.rightOpen = false,
    togglePin: () => shellState.rightPinned = !shellState.rightPinned
};

export const useAppShell = () => shell;


