from sqlalchemy import func, select
from nonix_web_db import AsyncSessionLocal
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..models.file_category import FileCategory
from ..models.file import File
from ..routers.file_category.file_category_schemas import FileCategoryCreate, FileCategoryUpdate, FileCategoryInDbModel, FileCategoryWithCountModel


class FileCategoryService(BaseCrudService):
    config = CRUDConfig(
        model=FileCategory,
        create_schema=FileCategoryCreate,
        update_schema=FileCategoryUpdate,
        response_schema=FileCategoryInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'slug']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['slug']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name', 'slug'],
            order_by='name'
        )
    )

    async def get_categories_with_file_counts(self):
        """Get categories with file counts using single SQL query"""
        async with AsyncSessionLocal() as session:
            query = select(
                FileCategory.id,
                FileCategory.name,
                FileCategory.slug,
                FileCategory.description,
                FileCategory.created_at,
                FileCategory.updated_at,
                func.count(File.id).label('file_count')
            ).outerjoin(File, FileCategory.id == File.category_id).group_by(
                FileCategory.id, 
                FileCategory.name, 
                FileCategory.slug, 
                FileCategory.description, 
                FileCategory.created_at, 
                FileCategory.updated_at
            )
            
            result = await session.execute(query)
            categories = []
            for row in result:
                category_data = FileCategoryWithCountModel(
                    id=row.id,
                    name=row.name,
                    slug=row.slug,
                    description=row.description,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    file_count=row.file_count
                )
                categories.append(category_data)
            
            return {"data": categories, "total": len(categories)}

