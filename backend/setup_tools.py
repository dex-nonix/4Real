#!/usr/bin/env python3
"""
Setup script to add tool records to the database.
Run this after starting the Flask app to populate the tools.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models.internal_tool import InternalTool
from app.models.persona_tool_access import PersonaToolAccess
from app.models.persona import Persona


def setup_tools():
    """Add all tool records to the database."""
    app = create_app()
    
    with app.app_context():
        print("🔧 Setting up LLM tools...")
        
        # Check if tools already exist
        existing_tools = InternalTool.query.count()
        if existing_tools > 1:  # More than just admin:system_info
            print(f"✅ Tools already exist ({existing_tools} found), skipping...")
            return
        
        # Define all tools
        tools_data = [
            # Artist tools
            ('artist', 'list_albums', 'artist:list_albums', 'List albums for an artist with pagination'),
            ('artist', 'get_info', 'artist:get_info', 'Get artist details and metadata'),
            
            # Album tools
            ('album', 'list_tracks', 'album:list_tracks', 'List tracks in an album'),
            ('album', 'get_info', 'album:get_info', 'Get album details and metadata'),
            
            # File tools
            ('file', 'list_artist_files', 'file:list_artist_files', 'List files for an artist'),
            ('file', 'read_lyrics', 'file:read_lyrics', 'Read lyric file content'),
            
            # Music tools
            ('track', 'list_by_album', 'track:list_by_album', 'List tracks in an album'),
            ('track', 'get_info', 'track:get_info', 'Get detailed track information'),
            ('style', 'list_all', 'style:list_all', 'List all music styles'),
        ]
        
        # Add tools
        for namespace, name, qualified_name, description in tools_data:
            # Check if tool already exists
            existing = InternalTool.query.filter_by(qualified_name=qualified_name).first()
            if existing:
                print(f"  ⚠️  Tool {qualified_name} already exists, skipping...")
                continue
            
            tool = InternalTool(
                namespace=namespace,
                name=name,
                qualified_name=qualified_name,
                description=description,
                is_active=True
            )
            db.session.add(tool)
            print(f"  ➕ Added tool: {qualified_name}")
        
        # Commit tools
        db.session.commit()
        print(f"✅ Added {len(tools_data)} tools to database")
        
        # Setup tool access for personas
        print("🔐 Setting up tool access permissions...")
        
        # Get all personas
        personas = Persona.query.all()
        if not personas:
            print("  ⚠️  No personas found, skipping access setup...")
            return
        
        for persona in personas:
            print(f"  👤 Setting up access for persona: {persona.name}")
            
            # Check if access already exists
            existing_access = PersonaToolAccess.query.filter_by(persona_id=persona.id).count()
            if existing_access > 0:
                print(f"    ⚠️  Access already configured for {persona.name}, skipping...")
                continue
            
            # Add access patterns
            access_patterns = [
                'artist:*',      # All artist tools
                'album:*',       # All album tools
                'file:*',        # All file tools
                'track:*',       # All track tools
                'style:*',       # All style tools
                'admin:*',       # Admin tools
            ]
            
            for pattern in access_patterns:
                access = PersonaToolAccess(
                    persona_id=persona.id,
                    pattern=pattern,
                    allow=True
                )
                db.session.add(access)
                print(f"    ➕ Added access: {pattern}")
        
        # Commit access
        db.session.commit()
        print("✅ Tool access permissions configured")
        
        print("\n🎉 Tool setup complete!")
        print(f"📊 Total tools: {InternalTool.query.count()}")
        print(f"👥 Personas with access: {Persona.query.count()}")


if __name__ == '__main__':
    setup_tools()
