import { createApp, h } from 'vue'
import App from '@/App.vue'
import router from '@/router'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primeflex/primeflex.css'

// API services (configure base URL from env)
import { API_BASE_URL } from '@/config.js'
import ArtistService from '@/services/ArtistService.js'
import PersonaService from '@/services/PersonaService.js'
import InternalToolService from '@/services/InternalToolService.js'
import PersonaToolAccessService from '@/services/PersonaToolAccessService.js'
import MCPServerService from '@/services/MCPServerService.js'
import PersonaMCPServerService from '@/services/PersonaMCPServerService.js'
import ChatSessionService from '@/services/ChatSessionService.js'
import ChatMessageService from '@/services/ChatMessageService.js'
import ToolInvocationLogService from '@/services/ToolInvocationLogService.js'

const app = createApp({ render: () => h(App) })
app.use(router)
app.use(PrimeVue)
app.use(ToastService)
// Provide service singletons (inline, no temp vars)
app.provide('artists', new ArtistService())
app.provide('personas', new PersonaService())
app.provide('internal-tools', new InternalToolService())
app.provide('persona-tool-access', new PersonaToolAccessService())
app.provide('mcp-servers', new MCPServerService())
app.provide('persona-mcp-servers', new PersonaMCPServerService())
app.provide('chat-sessions', new ChatSessionService())
app.provide('chat-messages', new ChatMessageService())
app.provide('tool-invocation-logs', new ToolInvocationLogService())
app.mount('#app')

