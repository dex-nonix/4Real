// CrudService.js - generic CRUD service extending BaseApiService
import BaseApiService from './BaseApiService.js'

export default class CrudService extends BaseApiService {
  constructor(entity, uiConfig = {}) {
    super()
    if (!entity) {
      throw new Error('CrudService requires an entity string')
    }
    this.entity = entity
    this.config = uiConfig
  }

  basePath() {
    return `/${this.entity}`
  }

  list(params = {}) {
    return super.get(this.basePath(), { query: params })
  }

  get(id) {
    return super.get(`${this.basePath()}/${encodeURIComponent(id)}`)
  }

  create(payload) {
    return super.post(this.basePath(), payload)
  }

  update(id, payload) {
    return super.put(`${this.basePath()}/${encodeURIComponent(id)}`, payload)
  }

  delete(id) {
    return super.delete(`${this.basePath()}/${encodeURIComponent(id)}`)
  }

  search(params = {}) {
    return super.get(`${this.basePath()}/search`, { query: params })
  }

  bulk(operation, payload = {}) {
    return super.post(`${this.basePath()}/bulk`, { operation, ...payload })
  }

  bulkDelete(ids = []) {
    return this.bulk('delete', { ids })
  }

  selectorList(params = {}) {
    return super.get(`${this.basePath()}/selector`, { query: params })
  }

  selectorGet(id) {
    return super.get(`${this.basePath()}/selector/${encodeURIComponent(id)}`)
  }
}


 