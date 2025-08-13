export const leftNavItems = [
  {
    label: 'Music',
    icon: 'pi pi-music',
    items: [
      { label: 'Home', icon: 'pi pi-home', to: { name: 'home' } },
      { label: 'Dynamic Form', icon: 'pi pi-file-edit', to: { name: 'dynamic-form' } },
      { label: 'Dynamic Table', icon: 'pi pi-table', to: { name: 'dynamic-table' } }
      ,{ label: 'Artists', icon: 'pi pi-user', to: '/artists' }
      ,{ label: 'Albums', icon: 'pi pi-list', to: '/albums' }
      ,{ label: 'Tracks', icon: 'pi pi-play', to: '/tracks' }
      ,{ label: 'Styles', icon: 'pi pi-tag', to: '/styles' }
      ,{ label: 'Rhyme Techniques', icon: 'pi pi-sliders-h', to: '/rhyme-techniques' }
      ,{ label: 'Chat', icon: 'pi pi-comments', to: { name: 'chat' } }
    ]
  },
  {
    label: 'AI',
    icon: 'pi pi-brain',
    items: [
      { label: 'Providers', icon: 'pi pi-cog', to: '/ai-providers' },
      { label: 'Model Mappings', icon: 'pi pi-sitemap', to: '/ai-model-mappings' },
      { label: 'Analysis Results', icon: 'pi pi-chart-bar', to: '/ai-analysis-results' },
      { label: 'Internal Tools', icon: 'pi pi-wrench', to: '/internal-tools' },
      { label: 'Persona Access', icon: 'pi pi-shield', to: '/persona-tool-access' },
      { label: 'MCP Servers', icon: 'pi pi-server', to: '/mcp-servers' },
      { label: 'Persona MCP', icon: 'pi pi-share-alt', to: '/persona-mcp-servers' }
    ]
  }
]


