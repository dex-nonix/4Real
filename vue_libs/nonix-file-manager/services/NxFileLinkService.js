import NxCrudService from '@nonix-crud/services/NxCrudService.js'

export default class NxFileLinkService extends NxCrudService {
    constructor(app) {
        super(app, 'file-links', {
            table: {
                columns: [
                    {field: 'file_id', header: 'File', type: 'file_preview_fk', props: {entity: 'files'}},
                    {field: 'status', header: 'Status', type: 'text'},
                    {field: 'comment', header: 'Comment', type: 'text'},
                    {field: 'sort_order', header: 'Order', type: 'number'}
                ]
            },
            form: {
                fields: [
                    {
                        key: 'file_id',
                        type: 'fk_select',
                        label: 'File',
                        required: true,
                        props: {entity: 'files', search: true}
                    },
                    {
                        key: 'status',
                        type: 'select',
                        label: 'Status',
                        required: true,
                        props: {options: ['prototype', 'snippet', 'final']}
                    },
                    {key: 'comment', type: 'text', label: 'Comment'},
                    {key: 'sort_order', type: 'number', label: 'Order'}
                ]
            }
        })
    }
}



