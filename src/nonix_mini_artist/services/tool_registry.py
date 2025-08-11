"""
Built-in tool registry for chat personas
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from ..crud.helper import CRUDHelper
from ..core.models import Artist, Album, Track, Style
from ..core.database import get_database

class ToolRegistry:
    """Registry of built-in tools for chat personas"""
    
    def __init__(self):
        """Initialize tool registry"""
        self.db = get_database()
        self.artist_crud = CRUDHelper(Artist)
        self.album_crud = CRUDHelper(Album)
        self.track_crud = CRUDHelper(Track)
        self.style_crud = CRUDHelper(Style)
        
        # Register all available tools
        self.tools = {
            # File operations
            'read_file': self._read_file,
            'list_directory': self._list_directory,
            'search_files': self._search_files,
            'read_lyrics': self._read_lyrics,
            
            # Database operations
            'query_artist_data': self._query_artist_data,
            'query_album_data': self._query_album_data,
            'query_track_data': self._query_track_data,
            'query_music_stats': self._query_music_stats,
            'search_music': self._search_music,
            
            # Content operations
            'edit_lyrics': self._edit_lyrics,
            'edit_track_info': self._edit_track_info,
            'edit_album_info': self._edit_album_info,
            
            # Analysis operations
            'analyze_music': self._analyze_music,
            'analyze_lyrics': self._analyze_lyrics,
            'compare_tracks': self._compare_tracks,
            
            # Generation operations
            'generate_description': self._generate_description,
            'generate_report': self._generate_report,
            'create_content': self._create_content
        }
        
        # Tool categories and descriptions
        self.tool_categories = {
            'file_operations': {
                'description': 'Read and search files',
                'tools': ['read_file', 'list_directory', 'search_files', 'read_lyrics']
            },
            'database_operations': {
                'description': 'Query and search music data',
                'tools': ['query_artist_data', 'query_album_data', 'query_track_data', 'query_music_stats', 'search_music']
            },
            'content_operations': {
                'description': 'Edit music content and metadata',
                'tools': ['edit_lyrics', 'edit_track_info', 'edit_album_info']
            },
            'analysis_operations': {
                'description': 'Analyze music and lyrics',
                'tools': ['analyze_music', 'analyze_lyrics', 'compare_tracks']
            },
            'generation_operations': {
                'description': 'Generate content and reports',
                'tools': ['generate_description', 'generate_report', 'create_content']
            }
        }
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with parameters"""
        if tool_name not in self.tools:
            return {
                'success': False,
                'error': f'Tool "{tool_name}" not found',
                'available_tools': list(self.tools.keys())
            }
        
        try:
            # Check artist-specific permissions if persona_id is provided
            if 'persona_id' in kwargs:
                from .persona_service import AIPersonaService
                persona_service = AIPersonaService()
                
                # Validate artist content access for content-modifying tools
                if tool_name in ['edit_lyrics', 'edit_track_info', 'edit_album_info']:
                    content_type = tool_name.replace('edit_', '').replace('_', '')
                    content_id = kwargs.get('track_id') or kwargs.get('album_id')
                    
                    if content_id:
                        has_access = await persona_service.validate_artist_content_access(
                            kwargs['persona_id'], content_type, content_id
                        )
                        if not has_access:
                            return {
                                'success': False,
                                'error': f'Access denied: You can only modify your own content',
                                'permission_required': 'artist_owner'
                            }
            
            tool_func = self.tools[tool_name]
            result = await tool_func(**kwargs)
            
            return {
                'success': True,
                'tool_name': tool_name,
                'result': result,
                'parameters': kwargs
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool_name': tool_name
            }
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tools"""
        return list(self.tools.keys())
    
    def get_tool_categories(self) -> Dict[str, Any]:
        """Get tool categories and descriptions"""
        return self.tool_categories
    
    def tool_exists(self, tool_name: str) -> bool:
        """Check if a tool exists"""
        return tool_name in self.tools
    
    # ============================================================================
    # FILE OPERATION TOOLS
    # ============================================================================
    
    async def _read_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Read file contents"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {'error': f'File not found: {file_path}'}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'file_path': str(path),
                'content': content,
                'size': len(content),
                'encoding': 'utf-8'
            }
        except Exception as e:
            return {'error': f'Failed to read file: {str(e)}'}
    
    async def _list_directory(self, directory_path: str, **kwargs) -> Dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                return {'error': f'Directory not found: {directory_path}'}
            
            items = []
            for item in path.iterdir():
                items.append({
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else None
                })
            
            return {
                'directory': str(path),
                'items': items,
                'total_items': len(items)
            }
        except Exception as e:
            return {'error': f'Failed to list directory: {str(e)}'}
    
    async def _search_files(self, search_path: str, pattern: str, **kwargs) -> Dict[str, Any]:
        """Search for files matching pattern"""
        try:
            path = Path(search_path)
            if not path.exists():
                return {'error': f'Search path not found: {search_path}'}
            
            matching_files = []
            for file_path in path.rglob(pattern):
                if file_path.is_file():
                    matching_files.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size
                    })
            
            return {
                'search_path': str(path),
                'pattern': pattern,
                'matching_files': matching_files,
                'total_matches': len(matching_files)
            }
        except Exception as e:
            return {'error': f'Failed to search files: {str(e)}'}
    
    async def _read_lyrics(self, track_id: int, **kwargs) -> Dict[str, Any]:
        """Read lyrics for a specific track"""
        try:
            track = await self.track_crud.get_by_id(track_id)
            if not track:
                return {'error': f'Track not found: {track_id}'}
            
            return {
                'track_id': track_id,
                'track_name': track.name,
                'album': track.album.title,
                'artist': track.album.artist.name,
                'raw_lyrics': track.raw_lyrics,
                'formatted_lyrics': track.formatted_lyrics
            }
        except Exception as e:
            return {'error': f'Failed to read lyrics: {str(e)}'}
    
    # ============================================================================
    # DATABASE OPERATION TOOLS
    # ============================================================================
    
    async def _query_artist_data(self, artist_id: Optional[int] = None, artist_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Query artist data"""
        try:
            if artist_id:
                artist = await self.artist_crud.get_by_id(artist_id)
            elif artist_name:
                artists = await self.artist_crud.search(name=artist_name)
                artist = artists[0] if artists else None
            else:
                return {'error': 'Must provide artist_id or artist_name'}
            
            if not artist:
                return {'error': 'Artist not found'}
            
            # Get artist's albums
            albums = await self.album_crud.search(artist_id=artist.id)
            
            return {
                'artist': {
                    'id': artist.id,
                    'name': artist.name,
                    'abbreviation': artist.abbreviation,
                    'persona': artist.persona,
                    'created_at': artist.created_at.isoformat()
                },
                'albums': [
                    {
                        'id': album.id,
                        'title': album.title,
                        'album_number': album.album_number,
                        'release_date': album.release_date.isoformat() if album.release_date else None
                    }
                    for album in albums
                ],
                'total_albums': len(albums)
            }
        except Exception as e:
            return {'error': f'Failed to query artist data: {str(e)}'}
    
    async def _query_album_data(self, album_id: Optional[int] = None, artist_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Query album data"""
        try:
            if album_id:
                album = await self.album_crud.get_by_id(album_id)
            elif artist_id:
                albums = await self.album_crud.search(artist_id=artist_id)
                album = albums[0] if albums else None
            else:
                return {'error': 'Must provide album_id or artist_id'}
            
            if not album:
                return {'error': 'Album not found'}
            
            # Get album tracks
            tracks = await self.track_crud.search(album_id=album.id)
            
            return {
                'album': {
                    'id': album.id,
                    'title': album.title,
                    'album_number': album.album_number,
                    'description': album.description,
                    'release_date': album.release_date.isoformat() if album.release_date else None,
                    'artist': album.artist.name
                },
                'tracks': [
                    {
                        'id': track.id,
                        'track_number': track.track_number,
                        'name': track.name,
                        'duration': track.duration
                    }
                    for track in tracks
                ],
                'total_tracks': len(tracks)
            }
        except Exception as e:
            return {'error': f'Failed to query album data: {str(e)}'}
    
    async def _query_track_data(self, track_id: int, **kwargs) -> Dict[str, Any]:
        """Query track data"""
        try:
            track = await self.track_crud.get_by_id(track_id)
            if not track:
                return {'error': f'Track not found: {track_id}'}
            
            return {
                'track': {
                    'id': track.id,
                    'track_number': track.track_number,
                    'name': track.name,
                    'duration': track.duration,
                    'album': track.album.title,
                    'artist': track.album.artist.name
                },
                'lyrics': {
                    'raw': track.raw_lyrics,
                    'formatted': track.formatted_lyrics
                }
            }
        except Exception as e:
            return {'error': f'Failed to query track data: {str(e)}'}
    
    async def _query_music_stats(self, **kwargs) -> Dict[str, Any]:
        """Query music collection statistics"""
        try:
            total_artists = await self.artist_crud.count()
            total_albums = await self.album_crud.count()
            total_tracks = await self.track_crud.count()
            total_styles = await self.style_crud.count()
            
            return {
                'total_artists': total_artists,
                'total_albums': total_albums,
                'total_tracks': total_tracks,
                'total_styles': total_styles,
                'average_tracks_per_album': total_tracks / total_albums if total_albums > 0 else 0
            }
        except Exception as e:
            return {'error': f'Failed to query music stats: {str(e)}'}
    
    async def _search_music(self, query: str, search_type: str = 'all', **kwargs) -> Dict[str, Any]:
        """Search music collection"""
        try:
            results = {
                'query': query,
                'search_type': search_type,
                'artists': [],
                'albums': [],
                'tracks': []
            }
            
            if search_type in ['all', 'artists']:
                # Search artists by name
                artists = await self.artist_crud.search(name__contains=query)
                results['artists'] = [
                    {'id': a.id, 'name': a.name, 'abbreviation': a.abbreviation}
                    for a in artists
                ]
            
            if search_type in ['all', 'albums']:
                # Search albums by title
                albums = await self.album_crud.search(title__contains=query)
                results['albums'] = [
                    {'id': a.id, 'title': a.title, 'artist': a.artist.name}
                    for a in albums
                ]
            
            if search_type in ['all', 'tracks']:
                # Search tracks by name
                tracks = await self.track_crud.search(name__contains=query)
                results['tracks'] = [
                    {'id': t.id, 'name': t.name, 'album': t.album.title, 'artist': t.album.artist.name}
                    for t in tracks
                ]
            
            return results
        except Exception as e:
            return {'error': f'Failed to search music: {str(e)}'}
    
    # ============================================================================
    # CONTENT OPERATION TOOLS
    # ============================================================================
    
    async def _edit_lyrics(self, track_id: int, new_lyrics: str, **kwargs) -> Dict[str, Any]:
        """Edit track lyrics with artist validation"""
        try:
            # Get track information
            track = await self.track_crud.get_by_id(track_id)
            if not track:
                return {'error': f'Track not found: {track_id}'}
            
            # Check if persona has permission to edit this track
            if 'persona_id' in kwargs:
                from .persona_service import AIPersonaService
                persona_service = AIPersonaService()
                
                has_access = await persona_service.validate_artist_content_access(
                    kwargs['persona_id'], 'track', track_id
                )
                if not has_access:
                    return {'error': 'Access denied: You can only edit your own tracks'}
            
            # Update lyrics
            await self.track_crud.update(track_id, raw_lyrics=new_lyrics)
            
            return {
                'success': True,
                'track_id': track_id,
                'track_name': track.name,
                'message': 'Lyrics updated successfully'
            }
        except Exception as e:
            return {'error': f'Failed to edit lyrics: {str(e)}'}
    
    async def _edit_track_info(self, track_id: int, **kwargs) -> Dict[str, Any]:
        """Edit track information with artist validation"""
        try:
            # Get track information
            track = await self.track_crud.get_by_id(track_id)
            if not track:
                return {'error': f'Track not found: {track_id}'}
            
            # Check if persona has permission to edit this track
            if 'persona_id' in kwargs:
                from .persona_service import AIPersonaService
                persona_service = AIPersonaService()
                
                has_access = await persona_service.validate_artist_content_access(
                    kwargs['persona_id'], 'track', track_id
                )
                if not has_access:
                    return {'error': 'Access denied: You can only edit your own tracks'}
            
            # Update track info
            update_data = {}
            for field in ['name', 'duration']:
                if field in kwargs:
                    update_data[field] = kwargs[field]
            
            if update_data:
                await self.track_crud.update(track_id, **update_data)
            
            return {
                'success': True,
                'track_id': track_id,
                'track_name': track.name,
                'updated_fields': list(update_data.keys()),
                'message': 'Track information updated successfully'
            }
        except Exception as e:
            return {'error': f'Failed to edit track info: {str(e)}'}
    
    async def _edit_album_info(self, album_id: int, **kwargs) -> Dict[str, Any]:
        """Edit album information with artist validation"""
        try:
            # Get album information
            album = await self.album_crud.get_by_id(album_id)
            if not album:
                return {'error': f'Album not found: {album_id}'}
            
            # Check if persona has permission to edit this album
            if 'persona_id' in kwargs:
                from .persona_service import AIPersonaService
                persona_service = AIPersonaService()
                
                has_access = await persona_service.validate_artist_content_access(
                    kwargs['persona_id'], 'album', album_id
                )
                if not has_access:
                    return {'error': 'Access denied: You can only edit your own albums'}
            
            # Update album info
            update_data = {}
            for field in ['title', 'description', 'release_date']:
                if field in kwargs:
                    update_data[field] = kwargs[field]
            
            if update_data:
                await self.album_crud.update(album_id, **update_data)
            
            return {
                'success': True,
                'album_id': album_id,
                'album_title': album.title,
                'updated_fields': list(update_data.keys()),
                'message': 'Album information updated successfully'
            }
        except Exception as e:
            return {'error': f'Failed to edit album info: {str(e)}'}
    
    # ============================================================================
    # ANALYSIS OPERATION TOOLS
    # ============================================================================
    
    async def _analyze_music(self, track_id: int, **kwargs) -> Dict[str, Any]:
        """Analyze music track"""
        try:
            track = await self.track_crud.get_by_id(track_id)
            if not track:
                return {'error': f'Track not found: {track_id}'}
            
            # Basic analysis (can be enhanced with AI later)
            analysis = {
                'track_id': track_id,
                'track_name': track.name,
                'album': track.album.title,
                'artist': track.album.artist.name,
                'duration': track.duration,
                'lyrics_length': len(track.raw_lyrics) if track.raw_lyrics else 0,
                'word_count': len(track.raw_lyrics.split()) if track.raw_lyrics else 0
            }
            
            return analysis
        except Exception as e:
            return {'error': f'Failed to analyze music: {str(e)}'}
    
    async def _analyze_lyrics(self, track_id: int, **kwargs) -> Dict[str, Any]:
        """Analyze track lyrics"""
        try:
            track = await self.track_crud.get_by_id(track_id)
            if not track:
                return {'error': f'Track not found: {track_id}'}
            
            if not track.raw_lyrics:
                return {'error': 'No lyrics available for analysis'}
            
            lyrics = track.raw_lyrics
            
            # Basic lyrics analysis
            analysis = {
                'track_id': track_id,
                'track_name': track.name,
                'total_characters': len(lyrics),
                'total_words': len(lyrics.split()),
                'total_lines': len(lyrics.split('\n')),
                'average_words_per_line': len(lyrics.split()) / len(lyrics.split('\n')) if lyrics.split('\n') else 0
            }
            
            return analysis
        except Exception as e:
            return {'error': f'Failed to analyze lyrics: {str(e)}'}
    
    async def _compare_tracks(self, track_ids: List[int], **kwargs) -> Dict[str, Any]:
        """Compare multiple tracks"""
        try:
            if len(track_ids) < 2:
                return {'error': 'Need at least 2 tracks to compare'}
            
            tracks = []
            for track_id in track_ids:
                track = await self.track_crud.get_by_id(track_id)
                if track:
                    tracks.append(track)
            
            if len(tracks) < 2:
                return {'error': 'Could not find enough tracks to compare'}
            
            # Compare tracks
            comparison = {
                'tracks': [
                    {
                        'id': t.id,
                        'name': t.name,
                        'album': t.album.title,
                        'artist': t.album.artist.name,
                        'duration': t.duration,
                        'lyrics_length': len(t.raw_lyrics) if t.raw_lyrics else 0
                    }
                    for t in tracks
                ],
                'comparison': {
                    'total_tracks': len(tracks),
                    'average_duration': sum(t.duration or 0 for t in tracks) / len(tracks) if tracks else 0,
                    'average_lyrics_length': sum(len(t.raw_lyrics or '') for t in tracks) / len(tracks) if tracks else 0
                }
            }
            
            return comparison
        except Exception as e:
            return {'error': f'Failed to compare tracks: {str(e)}'}
    
    # ============================================================================
    # GENERATION OPERATION TOOLS
    # ============================================================================
    
    async def _generate_description(self, content_type: str, content_id: int, **kwargs) -> Dict[str, Any]:
        """Generate description for content"""
        try:
            if content_type == 'track':
                content = await self.track_crud.get_by_id(content_id)
                if not content:
                    return {'error': f'Track not found: {content_id}'}
                
                description = f"Track '{content.name}' from album '{content.album.title}' by {content.album.artist.name}"
                if content.duration:
                    description += f" ({content.duration} seconds)"
                
            elif content_type == 'album':
                content = await self.album_crud.get_by_id(content_id)
                if not content:
                    return {'error': f'Album not found: {content_id}'}
                
                description = f"Album '{content.title}' by {content.artist.name}"
                if content.release_date:
                    description += f" (released {content.release_date})"
                
            else:
                return {'error': f'Unsupported content type: {content_type}'}
            
            return {
                'success': True,
                'content_type': content_type,
                'content_id': content_id,
                'generated_description': description
            }
        except Exception as e:
            return {'error': f'Failed to generate description: {str(e)}'}
    
    async def _generate_report(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Generate music collection report"""
        try:
            if report_type == 'collection_summary':
                stats = await self._query_music_stats()
                report = f"Music Collection Summary:\n"
                report += f"- Total Artists: {stats.get('total_artists', 0)}\n"
                report += f"- Total Albums: {stats.get('total_albums', 0)}\n"
                report += f"- Total Tracks: {stats.get('total_tracks', 0)}\n"
                report += f"- Total Styles: {stats.get('total_styles', 0)}\n"
                
                return {
                    'success': True,
                    'report_type': report_type,
                    'report': report,
                    'data': stats
                }
            else:
                return {'error': f'Unsupported report type: {report_type}'}
        except Exception as e:
            return {'error': f'Failed to generate report: {str(e)}'}
    
    async def _create_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Create new content (placeholder for future AI generation)"""
        try:
            if content_type == 'track_description':
                # This would integrate with AI service for content generation
                return {
                    'success': True,
                    'content_type': content_type,
                    'message': 'Content creation requires AI integration',
                    'placeholder': True
                }
            else:
                return {'error': f'Unsupported content type: {content_type}'}
        except Exception as e:
            return {'error': f'Failed to create content: {str(e)}'}
