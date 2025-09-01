from typing import Dict, Any, Optional

from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig
from nonix_web_agentic.llm.agentic_crud_tools import AgenticCrudTools
from nonix_web_agentic.llm.agentic_tools import tool
from ..models.style import Style
from ..services.style.style_schemas import StyleCreate, StyleUpdate


class StyleToolService(AgenticCrudTools):
    """Style management operations for artists."""

    prefix = "style"
    config = CRUDConfig(
        model=Style,
        create_schema=StyleCreate,
        update_schema=StyleUpdate,
        response_schema=StyleCreate,  # Use StyleCreate as response schema
        filters=FilterConfig(
            allowed_fields=['name', 'description', 'category'],
            search_fields=['name', 'description', 'category'],  # Fields to search by default
            context_aware=True
        ),
        sorting=SortingConfig(default_sort='name', allowed_fields=['name', 'category', 'created_at']),
        validation=ValidationConfig(unique_fields=['name'])
    )

    @tool("create")
    async def create_style(self, name: str, description: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Create a new music style/genre."""
        return await self.create(
            name=name,
            description=description,
            category=category
        )

    @tool("update")
    async def update_style(self, style_id: int, name: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing style's details."""
        return await self.update(
            item_id=style_id,
            name=name,
            description=description,
            category=category
        )

    @tool("delete")
    async def delete_style(self, style_id: int) -> Dict[str, Any]:
        """Delete a style."""
        return await self.delete(item_id=style_id)

    @tool("get")
    async def get_style(self, style_id: int) -> Dict[str, Any]:
        """Get details of a single style."""
        return await self.get(item_id=style_id)

    @tool("list")
    async def list_styles(self, **filters) -> Dict[str, Any]:
        """List all available styles with optional filtering."""
        return await self.list(**filters)

    @tool("assign")
    async def assign_style_to_track(self, artist_id: int, track_id: int, style_id: int) -> Dict[str, Any]:
        """Assign a style to a track."""
        from ..models.track import Track
        from nonix_web_db import AsyncSessionLocal
        from ..models.associations import TrackStyle
        
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}
            
            # Verify style exists
            style_result = await session.execute(
                self.config.model.__table__.select().where(self.config.model.id == style_id)
            )
            style = style_result.fetchone()
            if not style:
                return {"success": False, "error": "Style not found"}
            
            # Check if relationship already exists
            existing_result = await session.execute(
                TrackStyle.__table__.select().where(
                    TrackStyle.track_id == track_id, 
                    TrackStyle.style_id == style_id
                )
            )
            if existing_result.fetchone():
                return {"success": False, "error": "Style already assigned to this track"}
            
            # Create relationship
            track_style = TrackStyle(track_id=track_id, style_id=style_id)
            session.add(track_style)
            await session.commit()
            
            return {"success": True, "message": f"Style assigned to track"}

    @tool("remove")
    async def remove_style_from_track(self, artist_id: int, track_id: int, style_id: int) -> Dict[str, Any]:
        """Remove a style from a track."""
        from ..models.track import Track
        from nonix_web_db import AsyncSessionLocal
        from ..models.associations import TrackStyle
        
        async with AsyncSessionLocal() as session:
            # Verify track belongs to artist
            track_result = await session.execute(
                Track.__table__.select().where(Track.id == track_id, Track.artist_id == artist_id)
            )
            track = track_result.fetchone()
            if not track:
                return {"success": False, "error": "Track not found or doesn't belong to this artist"}
            
            # Remove relationship
            delete_result = await session.execute(
                TrackStyle.__table__.update()
                .where(
                    TrackStyle.track_id == track_id, 
                    TrackStyle.style_id == style_id
                )
                .values(active=False)
            )
            await session.commit()
            
            if delete_result.rowcount == 0:
                return {"success": False, "error": "Style was not assigned to this track"}
            
            return {"success": True, "message": f"Style removed from track"}

    @tool("tracks")
    async def list_tracks_with_style(self, artist_id: int, style_id: int) -> Dict[str, Any]:
        """List all tracks by an artist that have a specific style."""
        from ..models.track import Track
        from nonix_web_db import AsyncSessionLocal
        from ..models.associations import TrackStyle
        
        async with AsyncSessionLocal() as session:
            # Verify style exists
            style_result = await session.execute(
                self.config.model.__table__.select().where(self.config.model.id == style_id)
            )
            style = style_result.fetchone()
            if not style:
                return {"success": False, "error": "Style not found"}
            
            # Get tracks with this style
            tracks_result = await session.execute(
                Track.__table__.select()
                .join(TrackStyle, Track.id == TrackStyle.track_id)
                .where(Track.artist_id == artist_id, TrackStyle.style_id == style_id)
            )
            tracks = tracks_result.fetchall()
            
            return {
                "success": True,
                "style": {"id": style_id, "name": style.name},
                "tracks": [{"id": track.id, "title": track.title} for track in tracks],
                "total_tracks": len(tracks)
            }

    @tool("bulk_assign")
    async def bulk_assign_style_to_tracks(self, artist_id: int, track_ids: list, style_id: int) -> Dict[str, Any]:
        """Assign a style to multiple tracks at once."""
        from ..models.track import Track
        from nonix_web_db import AsyncSessionLocal
        from ..models.associations import TrackStyle
        
        async with AsyncSessionLocal() as session:
            # Verify style exists
            style_result = await session.execute(
                self.config.model.__table__.select().where(self.config.model.id == style_id)
            )
            style = style_result.fetchone()
            if not style:
                return {"success": False, "error": "Style not found"}
            
            # Verify all tracks belong to artist
            tracks_result = await session.execute(
                Track.__table__.select().where(
                    Track.id.in_(track_ids),
                    Track.artist_id == artist_id
                )
            )
            tracks = tracks_result.fetchall()
            if len(tracks) != len(track_ids):
                return {"success": False, "error": "Some tracks not found or don't belong to this artist"}
            
            # Check existing relationships and create new ones
            assigned_count = 0
            for track_id in track_ids:
                existing_result = await session.execute(
                    TrackStyle.__table__.select().where(
                        TrackStyle.track_id == track_id, 
                        TrackStyle.style_id == style_id
                    )
                )
                if not existing_result.fetchone():
                    track_style = TrackStyle(track_id=track_id, style_id=style_id)
                    session.add(track_style)
                    assigned_count += 1
            
            await session.commit()
            
            return {"success": True, "message": f"Style assigned to {assigned_count} tracks"}

    @tool("bulk_remove")
    async def bulk_remove_style_from_tracks(self, artist_id: int, track_ids: list, style_id: int) -> Dict[str, Any]:
        """Remove a style from multiple tracks at once."""
        from ..models.track import Track
        from nonix_web_db import AsyncSessionLocal
        from ..models.associations import TrackStyle
        
        async with AsyncSessionLocal() as session:
            # Verify all tracks belong to artist
            tracks_result = await session.execute(
                Track.__table__.select().where(
                    Track.id.in_(track_ids),
                    Track.artist_id == artist_id
                )
            )
            tracks = tracks_result.fetchall()
            if len(tracks) != len(track_ids):
                return {"success": False, "error": "Some tracks not found or don't belong to this artist"}
            
            # Remove style from all tracks
            delete_result = await session.execute(
                TrackStyle.__table__.delete().where(
                    TrackStyle.track_id.in_(track_ids),
                    TrackStyle.style_id == style_id
                )
            )
            await session.commit()
            
            return {"success": True, "message": f"Style removed from {delete_result.rowcount} tracks"}


# Create an instance for the plugin to use
style_tool_service = StyleToolService()
