#!/usr/bin/env python3
"""
Basic usage example for Nonix Mini Artist Manager
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nonix_mini_artist.core.database import init_database
from nonix_mini_artist.crud.helper import CRUDHelper
from nonix_mini_artist.services.music_service import MusicService
from nonix_mini_artist.core.models import Artist, Album, Track

async def main():
    """Main example function"""
    print("🎵 Nonix Mini Artist Manager - Basic Usage Example")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    init_database()
    print("✅ Database initialized!")
    
    # Create music service
    print("\n🎯 Creating music service...")
    music_service = MusicService()
    
    # Create an artist
    print("\n🎤 Creating artist...")
    artist = await music_service.create_artist(
        name="The Rolling Calf",
        abbreviation="TRC",
        persona="Dancehall legend from Jamaica"
    )
    print(f"✅ Artist created: {artist}")
    
    # Create an album
    print("\n💿 Creating album...")
    album = await music_service.create_album(
        artist_id=artist.id,
        album_number=1,
        title="Unleashed inna Di Streets",
        description="First album release"
    )
    print(f"✅ Album created: {album}")
    
    # Create a track
    print("\n🎵 Creating track...")
    track = await music_service.create_track(
        album_id=album.id,
        track_number=1,
        name="Rise From Ashes",
        raw_lyrics="Twelve... Di number of di beast reborn...",
        formatted_lyrics="[Intro]\nTwelve... Di number of di beast reborn..."
    )
    print(f"✅ Track created: {track}")
    
    # List all artists
    print("\n📋 Listing all artists...")
    artists = await music_service.list_artists()
    for artist in artists:
        print(f"  - {artist.name} ({artist.abbreviation})")
    
    # Get artist with albums and tracks
    print("\n🔍 Getting artist with full details...")
    artist_details = await music_service.get_artist_with_albums(artist.id)
    if artist_details:
        print(f"Artist: {artist_details['artist'].name}")
        for album_info in artist_details['albums']:
            print(f"  Album: {album_info['album'].title}")
            for track in album_info['tracks']:
                print(f"    Track: {track.name}")
    
    # Search functionality
    print("\n🔍 Searching for music...")
    search_results = await music_service.search_music("Rolling")
    print(f"Found {len(search_results['artists'])} artists, {len(search_results['albums'])} albums, {len(search_results['tracks'])} tracks")
    
    print("\n🎉 Example completed successfully!")
    print("\nTo run the full application:")
    print("  python main.py")

if __name__ == '__main__':
    asyncio.run(main())
