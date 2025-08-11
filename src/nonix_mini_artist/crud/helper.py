"""
Generic CRUD helper for any Peewee model
"""
from typing import List, Dict, Any, Optional, Type
from peewee import Model, Select, Query
from ..core.database import get_database

class CRUDHelper:
    """Generic CRUD operations for any Peewee model"""
    
    def __init__(self, model_class: Type[Model]):
        """Initialize with a model class"""
        self.model = model_class
        self.db = get_database()
    
    def _ensure_connection(self):
        """Ensure database connection is available"""
        if not self.db.is_closed():
            return
        self.db.connect()
    
    def _close_connection(self):
        """Close database connection if it's open"""
        if not self.db.is_closed():
            self.db.close()
    
    async def create(self, **kwargs) -> Model:
        """Create a new record"""
        try:
            self._ensure_connection()
            instance = self.model.create(**kwargs)
            return instance
        finally:
            self._close_connection()
    
    async def get_by_id(self, record_id: int) -> Optional[Model]:
        """Get record by ID"""
        try:
            self._ensure_connection()
            return self.model.get_by_id(record_id)
        except self.model.DoesNotExist:
            return None
        finally:
            self._close_connection()
    
    async def list_all(self, limit: Optional[int] = None) -> List[Model]:
        """List all records with optional limit"""
        try:
            self._ensure_connection()
            query = self.model.select()
            if limit:
                query = query.limit(limit)
            return list(query)
        finally:
            self._close_connection()
    
    async def update(self, record_id: int, **kwargs) -> Optional[Model]:
        """Update a record by ID"""
        try:
            self._ensure_connection()
            instance = self.model.get_by_id(record_id)
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        except self.model.DoesNotExist:
            return None
        finally:
            self._close_connection()
    
    async def delete(self, record_id: int) -> bool:
        """Delete a record by ID"""
        try:
            self._ensure_connection()
            instance = self.model.get_by_id(record_id)
            instance.delete_instance()
            return True
        except self.model.DoesNotExist:
            return False
        finally:
            self._close_connection()
    
    async def search(self, **filters) -> List[Model]:
        """Search records by filters"""
        try:
            self._ensure_connection()
            query = self.model.select()
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            return list(query)
        finally:
            self._close_connection()
    
    async def count(self) -> int:
        """Count total records"""
        try:
            self._ensure_connection()
            return self.model.select().count()
        finally:
            self._close_connection()
    
    async def exists(self, **filters) -> bool:
        """Check if record exists with given filters"""
        try:
            self._ensure_connection()
            query = self.model.select()
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            return query.exists()
        finally:
            self._close_connection()
