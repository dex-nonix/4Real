import NxBaseApiService from '@nonix-api/services/NxBaseApiService.js'

export default class NxCrudService extends NxBaseApiService {
  constructor(app, entity, uiConfig) {
    if (!entity) {
      throw new Error('NxCrudService requires an entity string')
    }
    if (!uiConfig) {
      throw new Error('NxCrudService requires an uiConfig ')
    }
    super(app)
    this.entity = entity
    this.config = this.#withDefaults(uiConfig)
  }

  #withDefaults(config) {
    const defaults = {
      table: {
        actions: ['view', 'edit', 'delete'],
        actionsDisplay: 'icons-only',
        bulkActions: ['delete', 'export'],
        paginated: true,
        pageSize: 20,
        selectionMode: 'multiple',
        resizable: true,
        striped: true,
        hover: true
      }
    }
    const merged = { ...config }
    merged.table = { ...defaults.table, ...(config.table || {}) }
    return merged
  }

  basePath() { return `/${this.entity}` }

  async list(params = {}) {
    return await super.get('/', { query: params })
  }

  async get(id) {
    return await super.get(`/${encodeURIComponent(id)}`)
  }

  async create(payload) {
    return await super.post('/', payload)
  }

  async update(id, payload) {
    return await super.put(`/${encodeURIComponent(id)}`, payload)
  }

  async delete(id) {
    return await super.delete(`/${encodeURIComponent(id)}`)
  }

  async search(params = {}) {
    return await super.get('/search', { query: params })
  }

  async bulk(operation, payload = {}) {
    return await super.post('/bulk', { operation, ...payload })
  }

  async bulkDelete(ids = []) {
    return await this.bulk('delete', { ids })
  }

  async selectorList(params = {}) {
    return await super.get('/selector', { query: params })
  }

  async selectorGet(id) {
    return await super.get(`/selector/${encodeURIComponent(id)}`)
  }
}


 