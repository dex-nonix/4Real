from typing import Dict, Any
import os
from ... import db
from ...models.file import File
from ...models.file_category import FileCategory
from ...models.artist import Artist


def file_list_artist_files(artist_id: int, category: str = None) -> Dict[str, Any]:
    """List files for an artist, optionally filtered by category."""
    try:
        # Verify artist exists
        artist = Artist.query.filter_by(id=artist_id).first()
        if not artist:
            return {'status': 'error', 'error': f'Artist {artist_id} not found'}
        
        # Build query
        query = File.query.filter_by(artist_id=artist_id)
        
        # Apply category filter if specified
        if category:
            category_obj = FileCategory.query.filter_by(name=category).first()
            if category_obj:
                query = query.filter_by(category_id=category_obj.id)
        
        # Get files ordered by creation date
        files = query.order_by(File.created_at.desc()).all()
        
        # Get categories for this artist
        categories = FileCategory.query.join(File).filter(File.artist_id == artist_id).distinct().all()
        
        return {
            'status': 'success',
            'result': {
                'artist': artist.to_dict(),
                'files': [file.to_dict() for file in files],
                'categories': [cat.to_dict() for cat in categories],
                'file_count': len(files),
                'filtered_by_category': category
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}


def file_read_lyrics(file_id: int) -> Dict[str, Any]:
    """Read lyric file content."""
    try:
        # Get file info
        file_obj = File.query.filter_by(id=file_id).first()
        if not file_obj:
            return {'status': 'error', 'error': f'File {file_id} not found'}
        
        # Check if it's a text/lyric file
        if not file_obj.mime_type or not file_obj.mime_type.startswith('text/'):
            return {'status': 'error', 'error': f'File {file_id} is not a text file'}
        
        # Read file content
        file_path = file_obj.file_path
        if not file_path or not os.path.exists(file_path):
            return {'status': 'error', 'error': f'File path {file_path} not found'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        return {
            'status': 'success',
            'result': {
                'file': file_obj.to_dict(),
                'content': content,
                'content_length': len(content),
                'lines': content.count('\n') + 1
            }
        }
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}
