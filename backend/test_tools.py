#!/usr/bin/env python3
"""
Simple test script to verify tool imports work correctly.
This doesn't require Flask to be running.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_tool_imports():
    """Test that all tool modules can be imported."""
    print("🧪 Testing tool imports...")
    
    try:
        # Test artist tools
        from app.services.tools.artist_tools import artist_list_albums, artist_get_info
        print("  ✅ Artist tools imported successfully")
        
        # Test album tools
        from app.services.tools.album_tools import album_list_tracks, album_get_info
        print("  ✅ Album tools imported successfully")
        
        # Test file tools
        from app.services.tools.file_tools import file_list_artist_files, file_read_lyrics
        print("  ✅ File tools imported successfully")
        
        # Test music tools
        from app.services.tools.music_tools import track_list_by_album, style_list_all, track_get_info
        print("  ✅ Music tools imported successfully")
        
        # Test registry
        from app.services.internal_tool_registry import registry
        print("  ✅ Tool registry imported successfully")
        
        # Check registered tools
        tools = registry.list()
        print(f"  📊 Registry contains {len(tools)} tools:")
        for name in sorted(tools.keys()):
            print(f"    - {name}")
        
        print("\n🎉 All tool imports successful!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = test_tool_imports()
    sys.exit(0 if success else 1)
