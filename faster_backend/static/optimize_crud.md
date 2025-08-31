# CRUD System Optimization & Artist Tools Implementation Plan

## Overview
This document outlines the two-phase approach to:
1. **Phase 1**: Optimize the CRUD system to be fully DRY and reusable
2. **Phase 2**: Create artist-focused tools using the optimized CRUD system

## Phase 1: CRUD System Optimization

### Current State Analysis
- `GenericCRUDService` mixes HTTP logic with business logic
- CRUD operations are duplicated between service classes and tools
- Validation, query processing, and business logic scattered across services
- No clean separation between HTTP layer and core CRUD operations

### Target Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Layer (Thin)                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │  AlbumService   │ │  TrackService   │ │ ArtistService│  │
│  │  (HTTP Routes)  │ │  (HTTP Routes)  │ │ (HTTP Routes)│  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 CRUD Operations Layer                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ CRUDOperations  │ │ArtistCRUDOps    │ │ QueryBuilder │  │
│  │  (Pure Logic)   │ │(Artist Scoped)  │ │ (Filters)    │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │   Models        │ │   Schemas       │ │   Utils      │  │
│  │  (SQLAlchemy)   │ │  (Pydantic)     │ │ (CRUD Help)  │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step 1: Extract Core CRUD Operations
**File**: `faster_backend/nonix_web_db/crud/crud_operations.py`
```python
class CRUDOperations:
    def __init__(self, model, config: CRUDConfig):
        self.model = model
        self.config = config
    
    async def create(self, data: BaseModel, session: AsyncSession) -> ModelType
    async def update(self, item_id: int, data: BaseModel, session: AsyncSession) -> ModelType
    async def delete(self, item_id: int, session: AsyncSession)
    async def get_one(self, item_id: int, session: AsyncSession) -> ModelType
    async def get_all(self, query_params: dict, session: AsyncSession) -> Dict
    async def bulk_update(self, ids: List[int], data: dict, session: AsyncSession)
    async def _validate_unique_fields(self, data: BaseModel, item_id: Optional[int], session: AsyncSession)
```

#### Step 2: Create Artist-Scoped CRUD Operations
**File**: `faster_backend/nonix_web_db/crud/artist_crud_operations.py`
```python
class ArtistCRUDOperations(CRUDOperations):
    def __init__(self, model, config: CRUDConfig, artist_id: int):
        super().__init__(model, config)
        self.artist_id = artist_id
    
    async def create_for_artist(self, data: BaseModel, session: AsyncSession) -> ModelType
    async def list_for_artist(self, session: AsyncSession, filters: List = None, **kwargs) -> Dict
    async def update_for_artist(self, item_id: int, data: BaseModel, session: AsyncSession) -> ModelType
    async def delete_for_artist(self, item_id: int, session: AsyncSession)
    def _get_artist_filter(self)
    async def _verify_artist_ownership(self, item_id: int, session: AsyncSession)
```

#### Step 3: Refactor Existing Services
**Files to Update**:
- `faster_backend/nonix_web_music_artist/services/album/album_service.py`
- `faster_backend/nonix_web_music_artist/services/track/track_service.py`
- `faster_backend/nonix_web_music_artist/services/artist/artist_service.py`

**Changes**:
- Replace direct CRUD logic with calls to `CRUDOperations` instances
- Keep HTTP routing and request/response handling
- Remove duplicate business logic

#### Step 4: Update Generic CRUD Service
**File**: `faster_backend/nonix_web_db/crud/generic_crud_service.py`
- Make it inherit from or use `CRUDOperations`
- Keep HTTP-specific logic only
- Remove duplicate CRUD implementations

### Phase 1 Deliverables
- [ ] Core CRUD operations extracted to pure functions/classes
- [ ] Artist-scoped CRUD operations implemented
- [ ] All existing services refactored to use new CRUD layer
- [ ] No duplicate business logic between services and tools
- [ ] All existing functionality preserved and working
- [ ] Tests passing for both HTTP endpoints and internal operations

---

## Phase 2: Artist-Focused Tools Implementation

### Current State Analysis
- Tools like `style_list_all` have incorrect database queries
- No artist-scoped CRUD operations available to tools
- Tools duplicate business logic that should be in CRUD layer
- LLM tools not leveraging existing validation and schema system

### Target Tool Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Tools Layer                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ Album Tools     │ │  Track Tools    │ │ Style Tools  │  │
│  │ (Artist Scoped) │ │ (Artist Scoped) │ │(Artist Data) │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 CRUD Operations Layer                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ CRUDOperations  │ │ArtistCRUDOps    │ │ QueryBuilder │  │
│  │  (Pure Logic)   │ │(Artist Scoped)  │ │ (Filters)    │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step 1: Fix Existing Tools
**File**: `faster_backend/nonix_web_music_artist/llm_tools/music_tools.py`
- Fix `style_list_all` to use proper track-style relationships
- Remove hardcoded SQL queries
- Use existing CRUD utilities and models

#### Step 2: Create Artist-Scoped Tool Functions
**New Tools to Implement**:
```python
# Album Management
async def create_album_for_artist(artist_id: int, title: str, release_date: Optional[date]) -> Dict
async def list_artist_albums(artist_id: int, filters: Dict = None) -> Dict
async def update_album_for_artist(artist_id: int, album_id: int, **updates) -> Dict
async def delete_album_for_artist(artist_id: int, album_id: int) -> Dict

# Track Management
async def add_track_to_album(artist_id: int, album_id: int, title: str, track_number: int, lyrics: str = None) -> Dict
async def update_track_lyrics(artist_id: int, track_id: int, lyrics: str) -> Dict
async def list_album_tracks(artist_id: int, album_id: int) -> Dict
async def delete_track_for_artist(artist_id: int, track_id: int) -> Dict

# Style Management
async def list_artist_track_styles(artist_id: int) -> Dict
async def add_style_to_track(artist_id: int, track_id: int, style_name: str) -> Dict
async def remove_style_from_track(artist_id: int, track_id: int, style_name: str) -> Dict

# Artist Analytics
async def get_artist_summary(artist_id: int) -> Dict
async def get_artist_discography(artist_id: int) -> Dict
```

#### Step 3: Update Tool Registration
**File**: `faster_backend/nonix_web_music_artist/plugin.py`
- Register new artist-scoped tools
- Update existing tool registrations
- Ensure all tools use proper artist context

#### Step 4: Update Tool Descriptions
**Tool Descriptions Should Be Artist-Focused**:
- Instead of: "Get detailed information about an album"
- Use: "View details of one of your albums"
- Instead of: "List all tracks for a specific album"
- Use: "See all tracks on one of your albums"

### Phase 2 Deliverables
- [ ] All existing tools fixed and working correctly
- [ ] New artist-scoped CRUD tools implemented
- [ ] Tools use optimized CRUD layer (no duplicate logic)
- [ ] All tools properly artist-scoped and secure
- [ ] Tool descriptions updated to be artist-persona focused
- [ ] LLM can successfully execute all tools without errors
- [ ] Tools return proper data structures for LLM consumption

---

## Implementation Order & Dependencies

### Phase 1 Must Complete First
- CRUD system optimization is prerequisite for tool implementation
- Tools depend on the new CRUD operations classes
- Cannot implement artist-scoped tools without artist-scoped CRUD operations

### Testing Strategy
1. **Phase 1 Testing**: Ensure all existing HTTP endpoints work identically
2. **Phase 1 Integration**: Verify CRUD operations work from both services and tools
3. **Phase 2 Testing**: Test each new tool individually
4. **Phase 2 Integration**: Test full LLM tool execution flow

### Success Criteria
- **Phase 1**: Zero duplicate business logic, all existing functionality preserved
- **Phase 2**: LLM can successfully manage artist's music catalog using tools
- **Overall**: Clean, maintainable, DRY architecture that scales

---

## Notes
- Keep existing Pydantic schemas and validation rules
- Maintain backward compatibility for HTTP endpoints
- Focus on artist persona experience in tool descriptions
- Ensure proper error handling and security (artist ownership verification)
- Consider adding bulk operations for common artist workflows
