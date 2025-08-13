// CrudService.js - generic CRUD service extending BaseApiService
import BaseApiService from './BaseApiService.js'

export default class CrudService extends BaseApiService {
  constructor(options = {}) {
    const { baseURL, entity, endpoints = {}, ...rest } = options
    super({ baseURL, ...rest })
    this.entity = entity
    this.endpoints = this.#buildEndpoints(entity, endpoints)
  }

  #buildEndpoints(entity, overrides) {
    // BaseApiService.baseURL should include /api; endpoints here are relative to it
    const tpl = (p) => (entity ? `/${entity}${p}` : '')
    const base = {
      list: overrides.list || (entity ? tpl('') : ''),
      get: overrides.get || (entity ? tpl('/{id}') : ''),
      create: overrides.create || (entity ? tpl('') : ''),
      update: overrides.update || (entity ? tpl('/{id}') : ''),
      delete: overrides.delete || (entity ? tpl('/{id}') : ''),
      bulkDelete: overrides.bulkDelete || (entity ? tpl('/bulk-delete') : '')
    }
    return { ...base, ...overrides }
  }

  resolveEndpoint(template, vars = {}) {
    return template.replace(/\{(\w+)\}/g, (_, k) => encodeURIComponent(vars[k]))
  }

  list(params = {}) {
    return this.get(this.endpoints.list, { query: params })
  }

  getOne(id) {
    const path = this.resolveEndpoint(this.endpoints.get, { id })
    return super.get(path)
  }

  create(payload) {
    return super.post(this.endpoints.create, payload)
  }

  update(id, payload) {
    const path = this.resolveEndpoint(this.endpoints.update, { id })
    return super.put(path, payload)
  }

  deleteOne(id) {
    const path = this.resolveEndpoint(this.endpoints.delete, { id })
    return super.delete(path)
  }

  bulkDelete(ids) {
    return super.post(this.endpoints.bulkDelete, { ids })
  }

  search(params = {}) {
    const basePath = this.endpoints.list.endsWith('/') ? this.endpoints.list.slice(0, -1) : this.endpoints.list
    const path = `${basePath}/search`
    return super.get(path, { query: params })
  }

  selectorList(params = {}) {
    const basePath = this.endpoints.list.endsWith('/') ? this.endpoints.list.slice(0, -1) : this.endpoints.list
    const path = `${basePath}/selector`
    return super.get(path, { query: params })
  }

  selectorGet(id) {
    const basePath = this.endpoints.list.endsWith('/') ? this.endpoints.list.slice(0, -1) : this.endpoints.list
    const path = `${basePath}/selector/${encodeURIComponent(id)}`
    return super.get(path)
  }
}


