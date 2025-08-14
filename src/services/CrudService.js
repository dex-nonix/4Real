// CrudService.js - generic CRUD service extending BaseApiService
import BaseApiService from './BaseApiService.js'

export default class CrudService extends BaseApiService {
  constructor(entity, uiConfig) {
    if (!entity) {
      throw new Error('CrudService requires an entity string')
    }
    if (!uiConfig) {
      throw new Error('CrudService requires an uiConfig ')
    }
    super()
    this.entity = entity
    this.config = this.#withDefaults(uiConfig)
  }

  #withDefaults(config) {
    const defaults = {
      table: {
        actions: ['view', 'edit', 'delete'],
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

  list(params = {}) {
    return super.get('/', { query: params })
  }

  get(id) {
    return super.get(`/${encodeURIComponent(id)}`)
  }

  create(payload) {
    return super.post('/', payload)
  }

  update(id, payload) {
    return super.put(`/${encodeURIComponent(id)}`, payload)
  }

  delete(id) {
    return super.delete(`/${encodeURIComponent(id)}`)
  }

  search(params = {}) {
    return super.get('/search', { query: params })
  }

  bulk(operation, payload = {}) {
    return super.post('/bulk', { operation, ...payload })
  }

  bulkDelete(ids = []) {
    return this.bulk('delete', { ids })
  }

  selectorList(params = {}) {
    return super.get('/selector', { query: params })
  }

  selectorGet(id) {
    return super.get(`/selector/${encodeURIComponent(id)}`)
  }
}


 