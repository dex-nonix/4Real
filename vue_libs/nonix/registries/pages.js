export const NX_PAGES = {
  dashboard: {
    component: {
      header: { title: 'Dashboard' },
      layout: { rowClass: 'grid', gap: 'gap-3' },
      context: () => ({ mode: 'view' }),
      widgets: [
        { type: 'text_block', props: { text: 'Welcome to the dashboard', class: 'col-12' } },
        { type: 'json_view', props: { value: { ok: true }, class: 'col-12 md:col-6' } }
      ]
    },
    defaultProps: {}
  }
}


