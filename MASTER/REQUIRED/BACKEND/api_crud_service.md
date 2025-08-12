# 🚀 CrudService - Automatic CRUD Handler

## 🎯 **PURPOSE:**
**Generic CRUD service that automatically handles ALL CRUD operations based on configuration - just like your frontend CrudManager, but for the backend!**

## 🏗️ **ARCHITECTURE:**

### **Core Concept:**
- **Configuration-driven** - like frontend CrudManager
- **Automatic CRUD** - handles create, read, update, delete automatically
- **Path-based routing** - uses service path to determine operations
- **Configurable behavior** - different modes for different use cases

## 🔧 **IMPLEMENTATION:**

### **1. CrudService Base Class (relative paths only):**
```python
# services/crud_service.py
from flask import request, jsonify
from decorators import expose

class CrudService:
    """Generic CRUD service that handles ALL operations automatically"""
    
    def __init__(self, db_session, model_class, config=None):
        self.db = db_session
        self.model = model_class
        self.config = config or self._get_default_config()
    
    def _get_default_config(self):
        """Default CRUD configuration"""
        return {
            'operations': {
                'create': True,      # Enable POST /
                'read': True,        # Enable GET / and GET /{id}
                'update': True,      # Enable PUT /{id}
                'delete': True,      # Enable DELETE /{id}
                'list': True,        # Enable GET / (list all)
                'search': True,      # Enable GET /search
                'bulk': True,        # Enable POST /bulk
                'selector': True     # Enable GET /selector and /selector/{id} (optimized for dropdowns)
            },
            'filters': {
                'enabled': True,     # Enable filtering
                'fields': [],        # Fields that can be filtered
                'operators': ['eq', 'ne', 'gt', 'lt', 'like', 'in']
            },
            'pagination': {
                'enabled': True,     # Enable pagination
                'default_page_size': 20,
                'max_page_size': 100
            },
            'sorting': {
                'enabled': True,     # Enable sorting
                'default_sort': 'id',
                'allowed_fields': []
            },
            'validation': {
                'enabled': True,     # Enable validation
                'required_fields': [],
                'unique_fields': []
            },
            'selector': {
                'enabled': True,     # Enable selector optimization
                'fields': ['name'],  # Extra fields to return. NOTE: 'id' is ALWAYS included automatically
                'display_format': None,    # Custom display format (e.g., 'firstName + " " + lastName')
                'search_fields': ['name'], # Fields to search in for selector
                'limit': 100,              # Max items for selector (performance)
                'order_by': 'name'         # How to order selector items
            }
        }
    
    def register_routes(self):
        """Auto-register CRUD routes with RELATIVE paths (APIRouter provides base)."""
        ops = self.config['operations']
        
        # CREATE - POST /{path}
        if ops.get('create'):
            @expose('/', methods=['POST'])
            def create(self, request):
                return self._handle_create(request)
        
        # READ ALL - GET /{path}
        if ops.get('list'):
            @expose('/')
            def list_all(self, request):
                return self._handle_list(request)
        
        # READ ONE - GET /{path}/{id}
        if ops.get('read'):
            @expose('/{id}')
            def read_one(self, request, id):
                return self._handle_read(request, id)
        
        # UPDATE - PUT /{path}/{id}
        if ops.get('update'):
            @expose('/{id}', methods=['PUT'])
            def update(self, request, id):
                return self._handle_update(request, id)
        
        # DELETE - DELETE /{path}/{id}
        if ops.get('delete'):
            @expose('/{id}', methods=['DELETE'])
            def delete(self, request, id):
                return self._handle_delete(request, id)
        
        # SEARCH - GET /{path}/search
        if ops.get('search'):
            @expose('/search')
            def search(self, request):
                return self._handle_search(request)
        
        # BULK OPERATIONS - POST /{path}/bulk
        if ops.get('bulk'):
            @expose('/bulk', methods=['POST'])
            def bulk_operations(self, request):
                return self._handle_bulk(request)
        
        # SELECTOR - GET /{path}/selector (optimized for dropdowns)
        if ops.get('selector'):
            @expose('/selector')
            def selector(self, request):
                return self._handle_selector(request)
            
            # SINGLE SELECTOR - GET /{path}/selector/{id} (single item for ID references)
            @expose('/selector/{id}')
            def single_selector(self, request, id):
                return self._handle_single_selector(request, id)
    
    def _handle_create(self, request):
        """Handle POST /{path} - Create new record"""
        try:
            data = request.get_json()
            
            # Validation
            if self.config['validation']['enabled']:
                errors = self._validate_create_data(data)
                if errors:
                    return jsonify({'errors': errors}), 400
            
            # Create instance
            instance = self.model(**data)
            self.db.add(instance)
            self.db.commit()
            
            return jsonify({
                'message': 'Created successfully',
                'data': self._serialize(instance)
            }), 201
            
        except Exception as e:
            self.db.rollback()
            return jsonify({'error': str(e)}), 500
    
    def _handle_list(self, request):
        """Handle GET /{path} - List all records with filtering/pagination/sorting"""
        try:
            query = self.db.query(self.model)
            
            # Apply filters
            if self.config['filters']['enabled']:
                query = self._apply_filters(query, request.args)
            
            # Apply sorting
            if self.config['sorting']['enabled']:
                query = self._apply_sorting(query, request.args)
            
            # Apply pagination
            if self.config['pagination']['enabled']:
                page = int(request.args.get('page', 1))
                per_page = min(
                    int(request.args.get('per_page', self.config['pagination']['default_page_size'])),
                    self.config['pagination']['max_page_size']
                )
                
                pagination = query.paginate(
                    page=page, 
                    per_page=per_page, 
                    error_out=False
                )
                
                return jsonify({
                    'data': [self._serialize(item) for item in pagination.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev
                    }
                })
            
            # No pagination
            items = query.all()
            return jsonify({
                'data': [self._serialize(item) for item in items],
                'total': len(items)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_read(self, request, id):
        """Handle GET /{path}/{id} - Read single record"""
        try:
            instance = self.db.query(self.model).filter_by(id=id).first()
            
            if not instance:
                return jsonify({'error': 'Not found'}), 404
            
            return jsonify({
                'data': self._serialize(instance)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_update(self, request, id):
        """Handle PUT /{path}/{id} - Update record"""
        try:
            instance = self.db.query(self.model).filter_by(id=id).first()
            
            if not instance:
                return jsonify({'error': 'Not found'}), 404
            
            data = request.get_json()
            
            # Validation
            if self.config['validation']['enabled']:
                errors = self._validate_update_data(data, instance)
                if errors:
                    return jsonify({'errors': errors}), 400
            
            # Update fields
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.db.commit()
            
            return jsonify({
                'message': 'Updated successfully',
                'data': self._serialize(instance)
            })
            
        except Exception as e:
            self.db.rollback()
            return jsonify({'error': str(e)}), 500
    
    def _handle_delete(self, request, id):
        """Handle DELETE /{path}/{id} - Delete record"""
        try:
            instance = self.db.query(self.model).filter_by(id=id).first()
            
            if not instance:
                return jsonify({'error': 'Not found'}), 404
            
            self.db.delete(instance)
            self.db.commit()
            
            return jsonify({
                'message': 'Deleted successfully'
            })
            
        except Exception as e:
            self.db.rollback()
            return jsonify({'error': str(e)}), 500
    
    def _handle_search(self, request):
        """Handle GET /{path}/search - Search records"""
        try:
            query = request.args.get('q', '')
            fields = request.args.get('fields', '').split(',')
            
            if not query:
                return jsonify({'error': 'Search query required'}), 400
            
            # Build search query
            search_query = self.db.query(self.model)
            
            if fields:
                # Search in specific fields
                from sqlalchemy import or_
                conditions = []
                for field in fields:
                    if hasattr(self.model, field):
                        conditions.append(
                            getattr(self.model, field).ilike(f'%{query}%')
                        )
                if conditions:
                    search_query = search_query.filter(or_(*conditions))
            else:
                # Search in all string fields
                from sqlalchemy import or_
                conditions = []
                for column in self.model.__table__.columns:
                    if str(column.type).startswith('VARCHAR') or str(column.type).startswith('TEXT'):
                        conditions.append(column.ilike(f'%{query}%'))
                if conditions:
                    search_query = search_query.filter(or_(*conditions))
            
            # Apply pagination
            if self.config['pagination']['enabled']:
                page = int(request.args.get('page', 1))
                per_page = min(
                    int(request.args.get('per_page', self.config['pagination']['default_page_size'])),
                    self.config['pagination']['max_page_size']
                )
                
                pagination = search_query.paginate(
                    page=page, 
                    per_page=per_page, 
                    error_out=False
                )
                
                return jsonify({
                    'data': [self._serialize(item) for item in pagination.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages
                    }
                })
            
            # No pagination
            items = search_query.all()
            return jsonify({
                'data': [self._serialize(item) for item in items],
                'total': len(items)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_bulk(self, request):
        """Handle POST /{path}/bulk - Bulk operations"""
        try:
            data = request.get_json()
            operation = data.get('operation')
            ids = data.get('ids', [])
            
            if not operation or not ids:
                return jsonify({'error': 'Operation and IDs required'}), 400
            
            if operation == 'delete':
                # Bulk delete
                instances = self.db.query(self.model).filter(
                    self.model.id.in_(ids)
                ).all()
                
                for instance in instances:
                    self.db.delete(instance)
                
                self.db.commit()
                
                return jsonify({
                    'message': f'Deleted {len(instances)} records successfully'
                })
            
            elif operation == 'update':
                # Bulk update
                update_data = data.get('data', {})
                
                instances = self.db.query(self.model).filter(
                    self.model.id.in_(ids)
                ).all()
                
                for instance in instances:
                    for key, value in update_data.items():
                        if hasattr(instance, key):
                            setattr(instance, key, value)
                
                self.db.commit()
                
                return jsonify({
                    'message': f'Updated {len(instances)} records successfully'
                })
            
            else:
                return jsonify({'error': 'Invalid operation'}), 400
                
        except Exception as e:
            self.db.rollback()
            return jsonify({'error': str(e)}), 500
    
    def _handle_selector(self, request):
        """Handle GET /{path}/selector - Optimized list for dropdowns/selects"""
        try:
            query = self.db.query(self.model)
            
            # Apply search if provided
            search_query = request.args.get('q', '')
            if search_query and self.config['selector']['search_fields']:
                from sqlalchemy import or_
                conditions = []
                for field_name in self.config['selector']['search_fields']:
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        conditions.append(field.ilike(f'%{search_query}%'))
                if conditions:
                    query = query.filter(or_(*conditions))
            
            # Apply ordering
            order_field = self.config['selector']['order_by']
            if hasattr(self.model, order_field):
                field = getattr(self.model, order_field)
                query = query.order_by(field.asc())
            
            # Apply limit for performance
            limit = self.config['selector']['limit']
            query = query.limit(limit)
            
            # Get results
            items = query.all()
            
             # Format for selector (dropdown/select)
            selector_data = []
            for item in items:
                selector_item = {
                    'id': getattr(item, 'id'),      # ALWAYS included
                    'value': getattr(item, 'id'),   # ALWAYS maps to id
                    'label': self._format_selector_label(item)  # For display
                }
                
                # Add additional fields if specified
                for field_name in self.config['selector']['fields']:
                    if field_name != 'id' and hasattr(item, field_name):
                        selector_item[field_name] = getattr(item, field_name)
                
                selector_data.append(selector_item)
            
            return jsonify({
                'data': selector_data,
                'total': len(selector_data)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_single_selector(self, request, id):
        """Handle GET /{path}/selector/{id} - Single selector item for ID references"""
        try:
            instance = self.db.query(self.model).filter_by(id=id).first()
            
            if not instance:
                return jsonify({'error': 'Not found'}), 404
            
            # Format for selector (same format as list, but single item)
            selector_item = {
                'id': getattr(instance, 'id'),     # ALWAYS included
                'value': getattr(instance, 'id'),  # ALWAYS maps to id
                'label': self._format_selector_label(instance)  # For display
            }
            
            # Add additional fields if specified
            for field_name in self.config['selector']['fields']:
                if field_name != 'id' and hasattr(instance, field_name):
                    selector_item[field_name] = getattr(instance, field_name)
            
            return jsonify({
                'data': selector_item
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _format_selector_label(self, item):
        """Format the display label for selector items"""
        display_format = self.config['selector']['display_format']
        
        if display_format:
            # Custom format like 'firstName + " " + lastName'
            try:
                # Simple string formatting - replace field names with values
                label = display_format
                for field_name in self.config['selector']['fields']:
                    if field_name != 'id' and hasattr(item, field_name):
                        field_value = str(getattr(item, field_name))
                        label = label.replace(field_name, field_value)
                
                # Handle basic concatenation patterns
                label = label.replace(' + " " + ', ' ')
                label = label.replace(' + " " +', ' ')
                label = label.replace('+" " +', ' ')
                label = label.replace('+" "+', ' ')
                
                return label.strip()
            except:
                # Fallback to first non-id field
                pass
        
        # Default: use first non-id field as label
        for field_name in self.config['selector']['fields']:
            if field_name != 'id' and hasattr(item, field_name):
                return str(getattr(item, field_name))
        
        # Fallback: use ID
        return str(getattr(item, 'id'))
    
    def _apply_filters(self, query, args):
        """Apply filters to query based on request args"""
        for key, value in args.items():
            if key.startswith('filter_') and hasattr(self.model, key[7:]):
                field_name = key[7:]
                field = getattr(self.model, field_name)
                
                # Handle different filter operators
                if ':' in value:
                    operator, filter_value = value.split(':', 1)
                    
                    if operator == 'eq':
                        query = query.filter(field == filter_value)
                    elif operator == 'ne':
                        query = query.filter(field != filter_value)
                    elif operator == 'gt':
                        query = query.filter(field > filter_value)
                    elif operator == 'lt':
                        query = query.filter(field < filter_value)
                    elif operator == 'like':
                        query = query.filter(field.ilike(f'%{filter_value}%'))
                    elif operator == 'in':
                        values = filter_value.split(',')
                        query = query.filter(field.in_(values))
                else:
                    # Default to equals
                    query = query.filter(field == value)
        
        return query
    
    def _apply_sorting(self, query, args):
        """Apply sorting to query based on request args"""
        sort_field = args.get('sort', self.config['sorting']['default_sort'])
        sort_order = args.get('order', 'asc')
        
        if hasattr(self.model, sort_field):
            field = getattr(self.model, sort_field)
            
            if sort_order.lower() == 'desc':
                query = query.order_by(field.desc())
            else:
                query = query.order_by(field.asc())
        
        return query
    
    def _validate_create_data(self, data):
        """Validate data for creation"""
        errors = []
        
        # Check required fields
        for field in self.config['validation']['required_fields']:
            if field not in data or data[field] is None:
                errors.append(f'{field} is required')
        
        # Check unique fields
        for field in self.config['validation']['unique_fields']:
            if field in data:
                existing = self.db.query(self.model).filter(
                    getattr(self.model, field) == data[field]
                ).first()
                if existing:
                    errors.append(f'{field} must be unique')
        
        return errors
    
    def _validate_update_data(self, data, instance):
        """Validate data for update"""
        errors = []
        
        # Check unique fields (excluding current instance)
        for field in self.config['validation']['unique_fields']:
            if field in data:
                existing = self.db.query(self.model).filter(
                    getattr(self.model, field) == data[field],
                    self.model.id != instance.id
                ).first()
                if existing:
                    errors.append(f'{field} must be unique')
        
        return errors
    
    def _serialize(self, instance):
        """Serialize model instance to dict"""
        if hasattr(instance, 'to_dict'):
            return instance.to_dict()
        
        # Default serialization
        result = {}
        for column in instance.__table__.columns:
            result[column.name] = getattr(instance, column.name)
        return result
```

### **2. Entity Service Implementation:**
```python
# services/artist_service.py
from services.crud_service import CrudService
from models.artist import Artist

class ArtistService(CrudService):
    """Artist service with custom CRUD configuration"""
    
    def __init__(self, db_session):
        config = {
            'path': '/artists',
            'operations': {
                'create': True,
                'read': True,
                'update': True,
                'delete': True,
                'list': True,
                'search': True,
                'bulk': True
            },
            'filters': {
                'enabled': True,
                'fields': ['name', 'genre', 'country'],
                'operators': ['eq', 'ne', 'gt', 'lt', 'like', 'in']
            },
            'pagination': {
                'enabled': True,
                'default_page_size': 20,
                'max_page_size': 100
            },
            'sorting': {
                'enabled': True,
                'default_sort': 'name',
                'allowed_fields': ['name', 'genre', 'country', 'created_at']
            },
            'validation': {
                'enabled': True,
                'required_fields': ['name'],
                'unique_fields': ['name']
            },
            'selector': {
                'enabled': True,
                'fields': ['name', 'genre', 'country'],  # 'id' always included
                'display_format': 'name + " (" + genre + ")"',
                'search_fields': ['name', 'genre'],
                'limit': 50,
                'order_by': 'name'
            }
        }
        
        super().__init__(db_session, Artist, config)
        
        # Auto-register all CRUD routes
        self.register_routes()
    
    # Custom methods can still be added
    def get_by_genre(self, genre):
        """Custom method not covered by generic CRUD"""
        return self.db.query(self.model).filter_by(genre=genre).all()
```

### **3. Usage in Flask App:**
```python
# app.py
from flask import Flask
from services.api_router import APIRouter
from services.artist_service import ArtistService
from services.album_service import AlbumService

app = Flask(__name__)
api_router = APIRouter()

# Register services - CrudService auto-registers all CRUD routes
api_router.register_service('artists', ArtistService)
api_router.register_service('albums', AlbumService)

# Register APIRouter blueprint to /api
app.register_blueprint(api_router.blueprint, url_prefix='/api')

# DONE! All CRUD routes are auto-created:
# POST /api/artists - Create artist
# GET /api/artists - List artists (with filtering/pagination/sorting)
# GET /api/artists/{id} - Get artist by ID
# PUT /api/artists/{id} - Update artist
# DELETE /api/artists/{id} - Delete artist
# GET /api/artists/search - Search artists
# POST /api/artists/bulk - Bulk operations
```

## 📁 **FILE STRUCTURE:**

```
backend/
├── app/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_router.py        # Generic router
│   │   ├── crud_service.py      # Generic CRUD service
│   │   ├── artist_service.py    # Artist service with config
│   │   └── album_service.py     # Album service with config
│   ├── models/
│   │   ├── __init__.py
│   │   ├── artist.py            # Artist model
│   │   └── album.py             # Album model
│   └── decorators.py            # @expose decorator
├── config.py                     # Configuration
└── requirements.txt              # Dependencies
```

## 🎯 **KEY FEATURES:**

### **✅ Configuration-Driven:**
- **JSON config** defines what operations are enabled
- **Filters, pagination, sorting** all configurable
- **Validation rules** configurable per service
- **Different modes** for different use cases

### **✅ Automatic CRUD:**
- **All routes** created automatically
- **No manual implementation** needed
- **Standardized responses** across all operations
- **Error handling** built-in

### **✅ Advanced Features:**
- **Filtering** - `?filter_name=eq:John&filter_genre=in:rock,pop`
- **Pagination** - `?page=1&per_page=20`
- **Sorting** - `?sort=name&order=desc`
- **Search** - `?q=john&fields=name,genre`
- **Bulk operations** - delete/update multiple records
- **Selector optimization** - `?q=john` for dropdowns with custom display formats

### **✅ Extensible:**
- **Custom methods** can still be added
- **Override behavior** if needed
- **Inherit and extend** for complex cases
- **Config per service** for different needs

## 🎯 **SELECTOR FEATURES:**

### **✅ Optimized for Dropdowns/Selects:**
- **`GET /{path}/selector`** - Lightweight **list** for UI components
- **`GET /{path}/selector/{id}`** - **Single item** for ID references
- **Search support** - `?q=john` filters results
- **Custom display formats** - `firstName + " " + lastName`
- **Performance optimized** - limited results, minimal fields
- **Standardized response** - `{id, value, label, ...fields}` (same format for both)

### **✅ Display Format Examples:**
```python
# Simple concatenation
'display_format': 'firstName + " " + lastName'
# Result: "John Doe"

# With additional info
'display_format': 'name + " (" + genre + ")"'
# Result: "Metallica (Metal)"

# Complex format
'display_format': 'title + " - " + artist + " (" + year + ")"'
# Result: "Bohemian Rhapsody - Queen (1975)"
```

### **✅ Selector Response Format:**

#### **List Selector - `GET /{path}/selector`:**
```json
{
  "data": [
    {
      "id": 1,
      "value": 1,
      "label": "John Doe (Rock)",
      "name": "John Doe",
      "genre": "Rock",
      "country": "USA"
    }
  ],
  "total": 1
}
```

#### **Single Selector - `GET /{path}/selector/{id}`:**
```json
{
  "data": {
    "id": 1,
    "value": 1,
    "label": "John Doe (Rock)",
    "name": "John Doe",
    "genre": "Rock",
    "country": "USA"
  }
}
```

**Same object structure, but one instead of many!**

### **✅ Usage Examples:**

#### **1. Dropdown/Select List:**
```javascript
// Frontend - Get list for dropdown
fetch('/api/artists/selector?q=met')
  .then(response => response.json())
  .then(data => {
    // data.data = array of artists for dropdown
    data.data.forEach(artist => {
      console.log(`${artist.label} (ID: ${artist.id})`);
    });
  });
```

#### **2. Single Item Reference:**
```javascript
// Frontend - Get single item when you only have ID
fetch('/api/artists/selector/123')
  .then(response => response.json())
  .then(data => {
    // data.data = single artist object
    const artist = data.data;
    console.log(`Selected: ${artist.label}`);
    // Use artist.id, artist.name, artist.genre, etc.
  });
```

**Perfect for forms where you need to display selected values!**

## 🔄 **WORKFLOW:**

### **1. Create Service with Config:**
```python
class ArtistService(CrudService):
    def __init__(self, db_session):
        config = {
            'path': '/artists',
            'operations': {'create': True, 'read': True, 'update': True, 'delete': True},
            'filters': {'enabled': True, 'fields': ['name', 'genre']},
            'pagination': {'enabled': True, 'default_page_size': 20},
            'sorting': {'enabled': True, 'default_sort': 'name'},
            'validation': {'enabled': True, 'required_fields': ['name']}
        }
        super().__init__(db_session, Artist, config)
        self.register_routes()  # Auto-register all CRUD routes
```

### **2. Register Service:**
```python
api_router.register_service('artists', ArtistService)
```

### **3. All CRUD Routes Auto-Created:**
- **POST /api/artists** - Create
- **GET /api/artists** - List with filters/pagination/sorting
- **GET /api/artists/{id}** - Read one
- **PUT /api/artists/{id}** - Update
- **DELETE /api/artists/{id}** - Delete
- **GET /api/artists/search** - Search
- **POST /api/artists/bulk** - Bulk operations
- **GET /api/artists/selector** - List optimized for dropdowns/selects
- **GET /api/artists/selector/{id}** - Single item for ID references

## 📋 **CONFIGURATION EXAMPLES:**

### **1. Basic CRUD Service:**
```python
config = {
    'path': '/albums',
    'operations': {
        'create': True,
        'read': True,
        'update': True,
        'delete': True,
        'list': True,
        'search': True,
        'bulk': True
    }
}
```

### **2. Read-Only Service:**
```python
config = {
    'path': '/reports',
    'operations': {
        'create': False,
        'read': True,
        'update': False,
        'delete': False,
        'list': True,
        'search': True,
        'bulk': False
    }
}
```

### **3. Advanced Service:**
```python
config = {
    'path': '/tracks',
    'operations': {
        'create': True,
        'read': True,
        'update': True,
        'delete': True,
        'list': True,
        'search': True,
        'bulk': True,
        'selector': True
    },
    'filters': {
        'enabled': True,
        'fields': ['title', 'artist_id', 'album_id', 'genre', 'duration'],
        'operators': ['eq', 'ne', 'gt', 'lt', 'like', 'in', 'between']
    },
    'pagination': {
        'enabled': True,
        'default_page_size': 50,
        'max_page_size': 200
    },
    'sorting': {
        'enabled': True,
        'default_sort': 'title',
        'allowed_fields': ['title', 'artist_id', 'album_id', 'genre', 'duration', 'created_at']
    },
    'validation': {
        'enabled': True,
        'required_fields': ['title', 'artist_id'],
        'unique_fields': ['title', 'artist_id']
    },
    'selector': {
        'enabled': True,
        'fields': ['id', 'title', 'artist_id', 'genre'],
        'display_format': 'title + " - " + genre',
        'search_fields': ['title', 'genre'],
        'limit': 100,
        'order_by': 'title'
    }
}
```

## 🎯 **BENEFITS:**

### **✅ Configuration-Driven:**
- **Like frontend CrudManager** - config defines behavior
- **No code duplication** - same pattern for all entities
- **Easy to modify** - just change config, not code
- **Consistent behavior** - all services work the same way

### **✅ Automatic Everything:**
- **All CRUD routes** created automatically
- **Filtering, pagination, sorting** built-in
- **Validation, error handling** built-in
- **Bulk operations** built-in

### **✅ No Over-Engineering:**
- **One service class** handles all CRUD
- **Configuration** drives behavior
- **Inheritance** provides reusability
- **Just working, simple code**

### **✅ Frontend-Backend Consistency:**
- **Same patterns** - both use configuration
- **Same approach** - both avoid over-engineering
- **Same structure** - clean, logical organization

**This CrudService is EXACTLY like your frontend CrudManager - configuration-driven, automatic, and handles ALL the CRUD operations!** 🎉 