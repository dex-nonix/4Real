export const NX_ADVANCED_LEFT_SIDEBAR_ITEMS = [
  {
    label: 'Music',
    icon: 'pi pi-music',
    items: [
      { label: 'Home', icon: 'pi pi-home', to: { name: 'home' } },
      { label: 'Artists', icon: 'pi pi-user', to: '/artists' },
      { label: 'Albums', icon: 'pi pi-list', to: '/albums' }, 
      { label: 'Tracks', icon: 'pi pi-play', to: '/tracks' }, 
      { label: 'Styles', icon: 'pi pi-tag', to: '/styles' }, 
      { label: 'Rhyme Techniques', icon: 'pi pi-sliders-h', to: '/rhyme-techniques' },
    ]
  },
  {
    label: 'AI',
    icon: 'pi pi-brain',
    items: [
      { label: 'Providers', icon: 'pi pi-cog', to: '/ai-providers' },
      { label: 'Model Mappings', icon: 'pi pi-sitemap', to: '/ai-model-mappings' },
      { label: 'Analysis Results', icon: 'pi pi-chart-bar', to: '/ai-analysis-results' },
      { label: 'Chat Prompts', icon: 'pi pi-comments', to: '/chat-prompts' },
      { label: 'Internal Tools', icon: 'pi pi-wrench', to: '/internal-tools' },
      { label: 'Persona Access', icon: 'pi pi-shield', to: '/persona-tool-access' },
      { label: 'MCP Servers', icon: 'pi pi-server', to: '/mcp-servers' },
      { label: 'Persona MCP', icon: 'pi pi-share-alt', to: '/persona-mcp-servers' },
      { label: 'Personas', icon: 'pi pi-id-card', to: '/personas' },
      { label: 'Templates', icon: 'pi pi-file-text', to: '/templates' },
      { label: 'Chat Sessions', icon: 'pi pi-clock', to: '/chat-sessions' },
      { label: 'Chat Histories', icon: 'pi pi-history', to: '/chat-histories' },
      { label: 'Chat Messages', icon: 'pi pi-envelope', to: '/chat-messages' },
      { label: 'Tool Logs', icon: 'pi pi-book', to: '/tool-invocation-logs' }
    ]
  },
  
  {
    label: 'Media',
    icon: 'pi pi-image',
    items: [
      { label: 'File Categories', icon: 'pi pi-folder', to: '/file-categories' },
      { label: 'Files', icon: 'pi pi-file', to: '/files' },
      { label: 'File Links', icon: 'pi pi-link', to: '/file-links' }
    ]
  },
  {
    label: 'Examples',
    icon: 'pi pi-image',
    items: [
      { label: 'Dynamic Form', icon: 'pi pi-file-edit', to: { name: 'dynamic-form' } },
      { label: 'Dynamic Table', icon: 'pi pi-table', to: { name: 'dynamic-table' } },
      { label: 'Dashboard', icon: 'pi pi-chart-bar', to: '/dashboard' }
    ]
  }
]


