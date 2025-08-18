-- Add tools to internal_tools table
INSERT INTO internal_tools (namespace, name, qualified_name, description, is_active) VALUES
('artist', 'list_albums', 'artist:list_albums', 'List albums for an artist with pagination', 1),
('artist', 'get_info', 'artist:get_info', 'Get artist details and metadata', 1),
('album', 'list_tracks', 'album:list_tracks', 'List tracks in an album', 1),
('album', 'get_info', 'album:get_info', 'Get album details and metadata', 1),
('file', 'list_artist_files', 'file:list_artist_files', 'List files for an artist', 1),
('file', 'read_lyrics', 'file:read_lyrics', 'Read lyric file content', 1),
('track', 'list_by_album', 'track:list_by_album', 'List tracks in an album', 1),
('track', 'get_info', 'track:get_info', 'Get detailed track information', 1),
('style', 'list_all', 'style:list_all', 'List all music styles', 1);

-- Add tool access for all personas (replace persona_id with actual IDs from your personas table)
-- First, get your persona IDs:
-- SELECT id, name FROM personas;

-- Then run this for each persona (replace 1, 2, 3 with actual persona IDs):
INSERT INTO persona_tool_access (persona_id, pattern, allow) VALUES 
(1, 'artist:*', 1),
(1, 'album:*', 1),
(1, 'file:*', 1),
(1, 'track:*', 1),
(1, 'style:*', 1),
(1, 'admin:*', 1);

-- If you have more personas, repeat for each:
-- INSERT INTO persona_tool_access (persona_id, pattern, allow) VALUES 
-- (2, 'artist:*', 1),
-- (2, 'album:*', 1),
-- (2, 'file:*', 1),
-- (2, 'track:*', 1),
-- (2, 'style:*', 1),
-- (2, 'admin:*', 1);
