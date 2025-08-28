import os
from typing import Dict, Any, List
from sqlalchemy import select

from nonix_web_db import AsyncSessionLocal
from ..models.artist import Artist
from ..models.file import File
from ..models.file_category import FileCategory


async def file_list_artist_files(artist_id: int, category: str = None) -> Dict[str, Any]:
    """List files for a specific artist, optionally filtered by category."""
    async with AsyncSessionLocal() as db_session:
        artist_result = await db_session.execute(
            select(Artist).where(Artist.id == artist_id)
        )
        artist = artist_result.scalar_one_or_none()
        
        if not artist:
            return {"error": "Artist not found"}
        
        query = select(File).where(File.artist_id == artist_id)
        
        if category:
            category_obj_result = await db_session.execute(
                select(FileCategory).where(FileCategory.name == category)
            )
            category_obj = category_obj_result.scalar_one_or_none()
            
            if category_obj:
                query = query.where(File.category_id == category_obj.id)
        
        files_result = await db_session.execute(query)
        files = files_result.scalars().all()
        
        # Get unique categories for this artist
        categories_result = await db_session.execute(
            select(FileCategory).join(File).where(File.artist_id == artist_id).distinct()
        )
        categories = categories_result.scalars().all()
        
        return {
            "artist": artist.to_dict(),
            "files": [file.to_dict() for file in files],
            "categories": [cat.to_dict() for cat in categories],
            "total_files": len(files)
        }


async def file_read_lyrics(file_id: int) -> Dict[str, Any]:
    """Read lyrics content from a specific file."""
    async with AsyncSessionLocal() as db_session:
        file_obj_result = await db_session.execute(
            select(File).where(File.id == file_id)
        )
        file_obj = file_obj_result.scalar_one_or_none()
        
        if not file_obj:
            return {"error": "File not found"}
        
        # Read file content (assuming there's a method to read content)
        try:
            content = file_obj.read_content() if hasattr(file_obj, 'read_content') else "Content not available"
            return {
                "file": file_obj.to_dict(),
                "content": content,
                "content_length": len(content) if content else 0
            }
        except Exception as e:
            return {"error": f"Failed to read file content: {str(e)}"}
