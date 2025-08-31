# Better Music Management Tools - AI Optimized

## Core Philosophy
- **Simple, clear names** - no fancy marketing terms
- **AI-focused** - optimized for AI prompts and responses
- **Practical operations** - real music management workflows
- **Efficient message space** - short names, clear purpose

## Current Problems
1. **Generic CRUD** - basic create/update/delete instead of music operations
2. **Missing relationships** - can't add tracks to albums, manage track order
3. **Poor filtering** - no practical search/filter for large catalogs
4. **Unused tools** - some tools don't make sense for music workflow

## Proposed Tool Structure

### Album Management
- `album_create` - create new album
- `album_update` - update album details
- `album_delete` - delete album and tracks
- `album_get` - get album details
- `album_list` - list albums (with optional filters)
- `album_add_track` - add track to album
- `album_remove_track` - remove track from album
- `album_reorder` - change track order in album
- `album_tracks` - list all tracks in album

### Track Management
- `track_create` - create new track
- `track_update` - update track details
- `track_delete` - delete track
- `track_get` - get track details
- `track_list` - list tracks (with optional filters)
- `track_move` - move track between albums
- `track_position` - set track position in album

### Artist Management
- `artist_create` - create artist profile
- `artist_update` - update artist profile
- `artist_delete` - delete artist and all content
- `artist_get` - get artist details
- `artist_list` - list artists (with optional filters)
- `artist_catalog` - view all albums and tracks
- `artist_stats` - basic counts and metrics

### Style Management
- `style_create` - create new style
- `style_update` - update style details
- `style_delete` - delete style
- `style_get` - get style details
- `style_list` - list styles (with optional filters)
- `style_assign` - assign style to track
- `style_remove` - remove style from track
- `style_tracks` - list tracks with specific style

### Lyrics Management
- `lyrics_add` - add lyrics to track
- `lyrics_update` - update existing lyrics
- `lyrics_get` - retrieve track lyrics
- `lyrics_remove` - remove lyrics from track
- `lyrics_list` - list tracks with lyrics (with optional filters)

## Key Improvements

### 1. Relationship Management
- **Track-Album linking** - proper track addition/removal
- **Track ordering** - manage track sequence in albums
- **Bulk operations** - move multiple tracks at once

### 2. Practical Filtering
- **Track filtering** - by album, style, duration, lyrics
- **Album filtering** - by year, track count, style
- **Search functionality** - find content quickly

### 3. Workflow Operations
- **Track movement** - between albums, reordering
- **Lyrics workflow** - create, edit, manage
- **Album building** - assemble albums track by track

### 4. Data Efficiency
- **Smart queries** - get related data in one call
- **Context awareness** - always include relevant relationships
- **Minimal API calls** - optimize for AI conversation flow

### 5. Bulk Operations
- **Track management** - move multiple tracks at once
- **Style assignment** - apply styles to multiple tracks
- **Album operations** - bulk track operations within albums

## Implementation Priority

### Phase 1: Core CRUD + Relationships
1. `album_create`, `album_update`, `album_delete` - basic album management
2. `track_create`, `track_update`, `track_delete` - basic track management
3. `album_add_track`, `album_remove_track` - track-album relationships
4. `track_move`, `album_reorder` - track positioning and movement

### Phase 2: Enhanced Operations
1. `track_position` - set track positions in albums
2. `lyrics_add`, `lyrics_update`, `lyrics_remove` - complete lyrics management
3. `style_assign`, `style_remove` - style management
4. Enhanced filtering in list operations

### Phase 3: Advanced Features
1. `bulk_track_move` - move multiple tracks at once
2. `bulk_style_assign` - apply styles to multiple tracks
3. `artist_catalog`, `artist_stats` - catalog overview and statistics

## Tool Naming Convention
- **Format**: `entity_action` (e.g., `album_add_track`)
- **Keep it short** - no more than 3 words
- **Clear purpose** - obvious what the tool does
- **Consistent pattern** - easy for AI to remember

## Example Usage Scenarios

### Scenario 1: Building an Album
```
1. album_create("New Album", artist_id)
2. track_create("Song 1", album_id, artist_id)
3. album_add_track(album_id, track_id)
4. track_position(track_id, 1)
5. lyrics_add(track_id, "Song lyrics here")
```

### Scenario 2: Reorganizing Catalog
```
1. track_move(track_id, new_album_id)
2. album_reorder(new_album_id, [track1, track2, track3])
3. style_assign(track_id, style_id)
```

### Scenario 3: Content Discovery
```
1. track_search("love", artist_id)
2. lyrics_search("heart", artist_id)
3. album_tracks(album_id)
```

## Complete Tool Summary
- **Album Tools**: 9 methods (CRUD + relationship management)
- **Track Tools**: 8 methods (CRUD + positioning + movement)
- **Artist Tools**: 7 methods (CRUD + catalog + statistics)
- **Style Tools**: 8 methods (CRUD + assignment + discovery)
- **Lyrics Tools**: 5 methods (complete lyrics workflow)
- **Total**: 37 professional music management tools

## Benefits
- **Complete coverage** - all CRUD operations + relationship management
- **Professional naming** - clear, consistent, no marketing fluff
- **Efficient workflow** - logical operations for real artist needs
- **AI optimized** - short names, clear purpose, minimal message space
