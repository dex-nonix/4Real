# Nonix Mini Artist Manager

A simple, lightweight music metadata management system built with Python, SQLite, and NiceGUI. Perfect for managing your personal music collection with AI-powered insights.

## 🎯 What This Project Is About

**Nonix Mini Artist Manager** is a desktop application that helps you organize and manage music metadata for artists, albums, and tracks. It's designed to be:

- **Simple**: Clean, intuitive interface without enterprise complexity
- **Local**: SQLite database with no cloud dependencies
- **Smart**: AI-powered analysis using configurable LLM providers
- **Flexible**: Import from existing XML files, export to various formats
- **Fast**: Lightweight Python application with responsive UI

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NiceGUI UI    │    │   Peewee ORM    │    │  Generic LLM    │
│   (Frontend)    │◄──►│   (Database)    │◄──►│   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Layout     │    │   SQLite DB     │    │   LLM Providers │
│   & Components  │◄──►│   (Local File)  │    │   (OpenAI, etc) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Generic CRUD    │    │   Data Models   │
│   Helper        │◄──►│   (Artist, etc) │
└─────────────────┘    └─────────────────┘
```

## 📚 Libraries & Dependencies

### Core Dependencies
- **Python 3.8+** - Modern Python with async support
- **SQLite** - Local database storage
- **Peewee** - Simple, thread-safe ORM
- **NiceGUI** - Modern Python UI framework

### LLM Integration
- **LangChain** - AI/LLM orchestration framework
- **OpenAI** - GPT models for content analysis
- **Anthropic** - Claude models for detailed analysis
- **Local Models** - Ollama/other local LLM support

### Development & Utilities
- **Pydantic** - Data validation and settings
- **PyYAML** - Configuration file handling
- **aiofiles** - Async file operations
- **pytest** - Testing framework

## 🎵 Data Model

### Core Entities (Normalized Database Schema)
```
Artist (id, name, abbreviation, persona, image_path, created_at)
    ↓ (1:N)
Album (id, artist_id, album_number, title, description, cover_path, release_date)
    ↓ (1:N)
Track (id, album_id, track_number, name, raw_lyrics, formatted_lyrics, duration)
    ↓ (M:N via TrackStyle)
Style (id, name, category, description)
    ↓ (M:N via TrackRhymeTechnique)
RhymeTechnique (id, name, category, description)
    ↓ (1:N)
RhymeTechniqueGenre (id, rhyme_technique_id, genre, weight)
    ↓ (1:N)
RhymeTechniqueArtist (id, rhyme_technique_id, artist, weight)
```

### XML Structure Analysis
- **Artist**: `<name>`, `<abbreviation>`, `<alias-list>`, `<persona>` (CDATA with rich markdown)
- **Album**: `<albumNr>`, `<title>`, `<description>` (CDATA with track-by-track analysis)
- **Track**: `<name>`, `<trackNr>`, `<styles>` (includes/excludes), `<rawLyrics>`, `<lyrics>` (CDATA with formatted lyrics)

### Normalized Fields
- **Artist**: name, abbreviation, persona (rich markdown content), aliases (JSON array)
- **Album**: album_number, title, description (detailed track analysis), cover_path
- **Track**: track_number, name, raw_lyrics, formatted_lyrics, duration
- **Style**: name (reggae, dancehall, patwa, gun-shot, etc.), category, description
- **RhymeTechnique**: name, category (rhyme-types, rhyme-patterns, wordplay, structural-elements, flow-rhythm, rhetorical-devices), description
- **RhymeTechniqueGenre**: rhyme_technique_id, genre, weight (normalized genre weights)
- **RhymeTechniqueArtist**: rhyme_technique_id, artist, weight (normalized artist weights)

### Database Relationships
- **Artist → Album**: 1:N (one artist, many albums)
- **Album → Track**: 1:N (one album, many tracks)
- **Track ↔ Style**: M:N (many tracks can have many styles via TrackStyle junction table)
- **Track ↔ RhymeTechnique**: M:N (many tracks can have many rhyme techniques via TrackRhymeTechnique junction table)
- **RhymeTechnique → RhymeTechniqueGenre**: 1:N (one technique can have many genre weights)
- **RhymeTechnique → RhymeTechniqueArtist**: 1:N (one technique can have many artist weights)
- **Style**: Normalized table for musical styles/genres (no duplicates)
- **RhymeTechnique**: Normalized table for rhyme techniques from rhyme_techniques.json (no duplicates)

### Style Normalization (From XML Analysis)
- **Reggae**: reggae, dancehall, patwa
- **Effects**: dirty-dancehall fx, gun-shot
- **Genres**: dancehall, reggae dancehall
- **Cultural**: patwa (Jamaican dialect)

### Rhyme Technique Normalization (From rhyme_techniques.json)
- **Rhyme-Types**: end_rhyme, internal_rhyme, multi-syllabic_rhyme, slant_rhyme, eye_rhyme, chain_rhyme, monorhyme, enjambment_rhyme, masculine_rhyme, feminine_rhyme, triple_rhyme, rich_rhyme, identical_rhyme
- **Rhyme-Patterns**: couplet, alternate_rhyme, enclosed_rhyme, sporadic_rhyme, cross_rhyme, stacked_multis
- **Wordplay**: alliteration, assonance, consonance, pun, portmanteau, neologism, homophone, homograph, onomatopoeia
- **Structural-Elements**: anaphora, epiphora, refrain, call_and_response, parallelism, ad-lib
- **Flow-Rhythm**: syllable_density, on-beat, off-beat, polyrhythmic, stop_and_go, double_time, triplet_flow, syncopation
- **Rhetorical-Devices**: metaphor, simile, personification, irony, sarcasm, hyperbole, understatement, allusion, antithesis, imagery, allegory

## �� Features

### Core Functionality
- ✅ **Generic CRUD Helper**: Reusable CRUD operations for all entities
- ✅ **CRUD Operations**: Add, edit, delete artists/albums/tracks
- ✅ **Data Import**: Parse existing XML metadata files
- ✅ **Image Management**: Handle cover art and artist photos
- ✅ **Search & Filter**: Find music by various criteria

### AI-Powered Features
- 🤖 **Lyrics Analysis**: Sentiment, themes, cultural references
- 🤖 **Style Classification**: Auto-tagging based on content
- 🤖 **Content Generation**: Help with descriptions and bios
- 🤖 **Metadata Enhancement**: Improve existing data

### User Interface
- 🎨 **Reusable Layout**: Master layout with sidebar, header, content area
- 🧩 **Reusable Components**: Generic forms, tables, dialogs, search bars
- 📱 **Responsive Design**: Works on different screen sizes
- 🔍 **Advanced Search**: Find music quickly and easily
- 📊 **Data Visualization**: View your collection statistics
- 🎯 **Consistent UI**: Same look and feel across all views

## ��️ Development Setup

### Prerequisites
```bash
# Your existing virtual environment
/home/dex/Desktop/shadewalk/apps/artist_manager/.venv/bin/python

# Or create new one
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### Installation
```bash
# Clone and install in development mode
git clone <repository>
cd 4Real
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy `config/app.example.yaml` to `config/app.yaml`
2. Set your LLM API keys in environment variables
3. Configure database path in `config/database.yaml`

## 📁 Project Structure

```
4Real/
├── src/nonix_mini_artist/     # Main package
│   ├── core/                  # Database models & core logic
│   ├── crud/                  # Generic CRUD operations
│   ├── llm/                   # LLM service & providers
│   ├── ui/                    # NiceGUI interface
│   │   ├── layout/            # Reusable layout components
│   │   ├── components/        # Reusable UI components
│   │   ├── views/             # Entity-specific views
│   │   └── app.py             # Main application
│   ├── services/              # Business logic services
│   └── utils/                 # Utilities & helpers
├── examples/                   # Usage examples
├── tests/                     # Unit tests
├── config/                    # Configuration files
├── data/                      # Database storage
└── docs/                      # Documentation
```

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Set up project structure and packaging
- [ ] Implement Peewee ORM models
- [ ] Create basic database schema
- [ ] Set up configuration management

### Phase 2: Core Services (Week 2)
- [ ] Build generic CRUD helper system
- [ ] Implement music CRUD operations using generic helper
- [ ] Create XML import/export service
- [ ] Set up basic file management
- [ ] Add data validation

### Phase 3: LLM Integration (Week 3)
- [ ] Build generic LLM service architecture
- [ ] Implement provider abstractions
- [ ] Create configuration-driven LLM setup
- [ ] Add basic AI analysis features

### Phase 4: User Interface (Week 4)
- [ ] Build reusable layout system (sidebar, header, content)
- [ ] Create reusable UI components (forms, tables, dialogs, search)
- [ ] Implement entity-specific views using reusable components
- [ ] Add search, filtering, and data visualization
- [ ] Ensure consistent UI/UX across all views

### Phase 5: Polish & Testing (Week 5)
- [ ] Add error handling and validation
- [ ] Implement comprehensive testing
- [ ] Create usage examples
- [ ] Performance optimization

## �� Configuration

### LLM Providers
Configure different AI models for different tasks:

```yaml
# config/llm_presets.yaml
presets:
  lyrics_analyzer:
    provider: "openai"
    model: "gpt-4"
    system_prompt: "You are a music analyst..."
  
  style_classifier:
    provider: "anthropic"
    model: "claude-3-sonnet"
    system_prompt: "Classify music styles..."
```

### Database
```yaml
# config/database.yaml
database:
  path: "data/music.db"
  backup_enabled: true
  backup_interval: 24h
```

## �� Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=nonix_mini_artist
```

## 📖 Usage Examples

### Reusable UI Layout
```python
from nonix_mini_artist.ui.layout import MasterLayout
from nonix_mini_artist.ui.components import Sidebar, Header, ContentArea

# Master layout with reusable components
layout = MasterLayout()
layout.sidebar = Sidebar([
    {"title": "Artists", "icon": "🎤", "route": "/artists"},
    {"title": "Albums", "icon": "💿", "route": "/albums"},
    {"title": "Tracks", "icon": "🎵", "route": "/tracks"}
])
layout.header = Header(title="Music Manager", user_info=user)
layout.content = ContentArea()
```

### Reusable UI Components
```python
from nonix_mini_artist.ui.components import GenericTable, GenericForm, GenericDialog

# Generic table for any entity
table = GenericTable(
    data=artists,
    columns=["name", "abbreviation", "created_at"],
    actions=["edit", "delete", "view"]
)

# Generic form for any entity
form = GenericForm(
    model=Artist,
    fields=["name", "abbreviation", "description"],
    submit_action=create_artist
)
```

### Generic CRUD Helper (Backend)
```python
from nonix_mini_artist.crud.helper import CRUDHelper
from nonix_mini_artist.core.models import Artist

# Generic CRUD operations for any entity
crud = CRUDHelper(Artist)
artist = await crud.create(name="The Rolling Calf", abbreviation="TRC")
artists = await crud.list_all()
artist = await crud.get_by_id(1)
await crud.update(1, name="TRC Updated")
await crud.delete(1)

# Can be used by UI components, services, or directly
```

### Service Layer (Using Generic CRUD)
```python
from nonix_mini_artist.services.music_service import MusicService

# Create artist using generic CRUD
artist = await music_service.create_artist(
    name="The Rolling Calf",
    abbreviation="TRC",
    description="Dancehall legend from Jamaica"
)
```

### UI Components Using Generic CRUD
```python
from nonix_mini_artist.ui.components import GenericTable
from nonix_mini_artist.crud.helper import CRUDHelper

# UI table that uses generic CRUD operations
artist_crud = CRUDHelper(Artist)
table = GenericTable(
    data=await artist_crud.list_all(),
    crud_operations=artist_crud,  # Table can do CRUD directly
    columns=["name", "abbreviation", "created_at"]
)
```

### LLM Analysis
```python
from nonix_mini_artist.llm.service import LLMService

# Analyze lyrics
analysis = await llm.invoke(
    "lyrics_analyzer",
    "Analyze these dancehall lyrics for themes",
    system_prompt="Focus on Jamaican culture and street themes"
)
```

## �� Contributing

This is a personal project, but contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - feel free to use and modify for your own projects.

## 🆘 Support

- **Issues**: Create GitHub issues for bugs or feature requests
- **Documentation**: Check the `docs/` folder for detailed guides
- **Examples**: Look at `examples/` folder for usage patterns

---

**Nonix Mini Artist Manager** - Simple music metadata management with AI-powered insights! 🎵✨