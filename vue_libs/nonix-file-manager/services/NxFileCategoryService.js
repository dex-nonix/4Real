import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class NxFileCategoryService extends NxCrudService {
    constructor(app) {
        super(app, 'file-categories', {
            table: {
                columns: [
                    {field: 'name', header: 'Name', type: 'text', sortable: true},
                    {field: 'slug', header: 'Slug', type: 'text', sortable: true},
                    {field: 'description', header: 'Description', type: 'text'}
                ],
                actions: ['view', 'edit', 'delete'],
                bulkActions: ['delete', 'export'],
                filters: ['search'],
                paginated: true,
                pageSize: 20,
                selectionMode: 'multiple',
                resizable: true,
                striped: true,
                hover: true
            },
            form: {
                fields: [
                    {key: 'name', type: 'text', label: 'Name', required: true},
                    {key: 'slug', type: 'text', label: 'Slug'},
                    {key: 'description', type: 'text', label: 'Description'}
                ]
            }
        })
    }
}



