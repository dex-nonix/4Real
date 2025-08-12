# Nonix Mini Artist Manager

A powerful music metadata management system built with Python, SQLite, NiceGUI, and **Google AI integration**. Features complete runtime management of AI settings with zero restart required.

## 🎯 What This Project Is About

**Nonix Mini Artist Manager** is a desktop application that helps you organize and manage music metadata for artists, albums, and tracks with **intelligent AI-powered analysis**. It's designed to be:

- **Simple**: Clean, intuitive interface without enterprise complexity
- **Local**: SQLite database with no cloud dependencies
- **Smart**: **Google AI-powered analysis** using configurable providers
- **Flexible**: Import from existing XML files, export to various formats
- **Fast**: Lightweight Python application with responsive UI
- **Runtime Configurable**: **All AI settings changeable via UI without restart**

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NiceGUI UI    │    │   Peewee ORM    │    │  Google AI      │
│   (Frontend)    │◄──►│   (Database)    │◄──►│   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Layout     │    │   SQLite DB     │    │   AI Providers  │
│   & Components  │◄──►│   (Local File)  │    │   (Gemini,      │
└─────────────────┘    └─────────────────┘    │   Vertex AI)    │
         │                       │           └─────────────────┘
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

### **Google AI Integration** 🚀
- **Google Generative AI** - Gemini models for content analysis
- **Google Cloud Vertex AI** - Enterprise AI services
- **Pydantic-Settings** - Runtime configuration management
- **Async AI Providers** - Hot-swappable AI services

### Development & Utilities
- **Pydantic** - Data validation and settings
- **PyYAML** - Configuration file handling
- **aiofiles** - Async file operations
- **python-dotenv** - Environment variable management

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

## 🚀 Features

### Core Functionality
- ✅ **Generic CRUD Helper**: Reusable CRUD operations for all entities
- ✅ **CRUD Operations**: Add, edit, delete artists/albums/tracks
- ✅ **Data Import**: Parse existing XML metadata files
- ✅ **Image Management**: Handle cover art and artist photos
- ✅ **Search & Filter**: Find music by various criteria


### **Runtime AI Management** ⚡
- ✅ **Hot-Swappable Providers**: Switch between Google AI services instantly
- ✅ **Runtime API Key Changes**: Modify API keys without restart
- ✅ **Live Preset Management**: Create/modify AI presets in real-time
- ✅ **Dynamic Configuration**: All AI settings changeable via UI
- ✅ **Connection Testing**: Verify AI connections instantly
- ✅ **Usage Monitoring**: Track API usage and costs in real-time

### User Interface
- 🎨 **Reusable Layout**: Master layout with sidebar, header, content area
- 🧩 **Reusable Components**: Generic forms, tables, dialogs, search bars
- 📱 **Responsive Design**: Works on different screen sizes
- 🔍 **Advanced Search**: Find music quickly and easily
- 📊 **Data Visualization**: View your collection statistics
- 🎯 **Consistent UI**: Same look and feel across all views
- 🤖 **AI Settings View**: Complete AI configuration management

## 🎯 **Implementation Status: COMPLETE!** ✅

### **All Phases Completed:**
- ✅ **Phase 1**: Foundation & Database Models
- ✅ **Phase 2**: Core CRUD Operations
- ✅ **Phase 3**: Google AI Integration
- ✅ **Phase 4**: UI Foundation & Components
- ✅ **Phase 5**: Google AI UI Integration
- ✅ **Phase 6**: Advanced AI Features
- ✅ **Phase 7**: Runtime Management & Advanced Features

**The system is now a fully functional AI-powered music manager with enterprise-grade runtime management capabilities!**

---

## 🚀 **New Extension: AI Chat System** 🎭

**Status**: 🚧 **In Development** - Adding AI-powered chat with multiple personas

### **What's New:**
- **AI Personas**: Chat with different AI personalities (artists, assistants, analysts)
- **Multi-Chat Interface**: Sidebar with tabs for different conversations
- **Persistent History**: Each persona maintains separate chat history
- **Tool Integration**: Built-in tools for music management through chat
- **Artist Self-Management**: Artists can manage their content through natural language

### **Tracking Files:**
- 📋 **[CHAT_EXTENSION.md](CHAT_EXTENSION.md)** - Feature overview and current status
- 📋 **[CHAT_PHASES.md](CHAT_PHASES.md)** - Implementation phases and progress

### **Current Progress:**
- **Phase 1-4**: Database, Services, Tools & UI - ✅ **Complete** (50% complete)
- **Timeline**: 4-5 weeks for complete implementation
- **Priority**: High - Core feature for artist self-management

## 🚀 Quick Start

### **Easy Startup Scripts** 🎯

We've created multiple startup scripts for easy launching:

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Any platform:**
```bash
python start.py
```

### **What the Startup Scripts Do:**
1. ✅ **Check Python installation** and version compatibility
2. 🔧 **Auto-detect and activate** virtual environments (venv/.venv)
3. 📦 **Verify dependencies** (tkinter, sqlite3, etc.)
4. 🔍 **Find the correct entry point** (main.py or UI app)
5. 🚀 **Launch the application** with proper error handling
6. 💬 **Provide clear feedback** with emojis and status messages

### **Manual Setup (Alternative)**

#### Prerequisites
```bash
# Your existing virtual environment
/home/dex/Desktop/shadewalk/apps/artist_manager/.venv/bin/python

# Or create new one
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

#### Installation
```bash
# Clone and install in development mode
git clone <repository>
cd 4Real
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### **Google AI Configuration** 🔑
1. **Set Google AI API Key**:
   ```bash
   export GOOGLE_API_KEY="your_google_api_key_here"
   ```
2. **For Vertex AI** (optional):
   ```bash
   export GOOGLE_PROJECT_ID="your_project_id"
   export GOOGLE_LOCATION="us-central1"
   ```
3. **Or use the UI**: All settings configurable via AI Settings view!

## 📁 Project Structure

```
4Real/
├── 🚀 Startup Scripts         # Easy application launching
│   ├── start.sh               # Linux/macOS shell script
│   ├── start.py               # Cross-platform Python script
│   └── start.bat              # Windows batch file
├── src/nonix_mini_artist/     # Main package
│   ├── core/                  # Database models & core logic
│   ├── crud/                  # Generic CRUD operations
│   ├── ai/                    # Google AI service & providers
│   │   ├── providers/         # AI provider implementations
│   │   │   ├── base.py        # Abstract base provider
│   │   │   ├── gemini_provider.py    # Google Gemini
│   │   │   └── vertex_provider.py    # Google Vertex AI
│   │   ├── models.py          # AI data models
│   │   └── service.py         # Main AI service
│   ├── ui/                    # NiceGUI interface
│   │   ├── layout/            # Reusable layout components
│   │   ├── components/        # Reusable UI components
│   │   ├── views/             # Entity-specific views
│   │   │   ├── ai_settings_view.py   # AI configuration UI
│   │   │   └── tracks_view.py        # AI analysis integration
│   │   └── app.py             # Main application
│   ├── services/              # Business logic services
│   └── utils/                 # Utilities & helpers
├── examples/                   # Usage examples
├── config/                    # Configuration files
│   └── ai_config.json         # AI providers & presets
├── data/                      # Database storage
├── docs/                      # Documentation
├── artists/                   # Sample music data
│   └── TRC/                   # The Rolling Calf artist data
│       ├── albums/            # Album collections
│       └── artist.md          # Artist information
└── requirements.txt            # Python dependencies
```

## 🎯 **Implementation Roadmap - COMPLETED!** ✅

### **Phase 1: Foundation (Week 1)** ✅
- ✅ Set up project structure and packaging
- ✅ Implement Peewee ORM models
- ✅ Create basic database schema
- ✅ Set up configuration management

### **Phase 2: Core Services (Week 2)** ✅
- ✅ Build generic CRUD helper system
- ✅ Implement music CRUD operations using generic helper
- ✅ Create XML import/export service
- ✅ Set up basic file management
- ✅ Add data validation

### **Phase 3: Google AI Integration (Week 3)** ✅
- ✅ Build generic AI service architecture
- ✅ Implement Google AI providers (Gemini, Vertex AI)
- ✅ Create configuration-driven AI setup
- ✅ Add basic AI analysis features
- ✅ Runtime configuration management

### **Phase 4: User Interface (Week 4)** ✅
- ✅ Build reusable layout system (sidebar, header, content)
- ✅ Create reusable UI components (forms, tables, dialogs, search)
- ✅ Implement entity-specific views using reusable components
- ✅ Add search, filtering, and data visualization
- ✅ Ensure consistent UI/UX across all views

### **Phase 5: Google AI UI Integration (Week 5)** ✅
- ✅ Integrate AI capabilities into UI
- ✅ Add AI settings management view
- ✅ Implement runtime provider switching
- ✅ Add AI analysis actions to existing views
- ✅ Create AI analysis result displays

### **Phase 6: Advanced AI Features (Week 6)** ✅
- ✅ Intelligent content generation
- ✅ AI-powered style classification
- ✅ Smart search with AI understanding
- ✅ AI-driven metadata enhancement
- ✅ AI-powered content recommendations

### **Phase 7: Runtime Management (Week 7)** ✅
- ✅ Complete runtime AI configuration
- ✅ Hot-swappable providers
- ✅ Live preset management
- ✅ Real-time configuration updates
- ✅ Professional-grade AI management

## 🔧 **Configuration**

### **Google AI Providers** 🚀
Configure different AI models for different tasks:

```json
// config/ai_config.json
{
  "providers": [
    {
      "name": "gemini",
      "api_key": "your_google_api_key",
      "enabled": true
    },
    {
      "name": "vertex",
      "project_id": "your_project_id",
      "location": "us-central1",
      "enabled": false
    }
  ],
  "presets": [
    {
      "name": "lyrics_analyzer",
      "provider": "gemini",
      "model": "gemini-1.5-pro",
      "system_prompt": "You are a music analyst specializing in dancehall and reggae music...",
      "temperature": 0.7,
      "max_tokens": 1000
    }
  ]
}
```

### **Runtime Management** ⚡
- **API Keys**: Change without restart
- **Providers**: Add/edit/delete on the fly
- **Presets**: Create custom analysis types
- **Settings**: All configurable via UI

### Database
```yaml
# config/database.yaml
database:
  path: "data/music.db"
  backup_enabled: true
  backup_interval: 24h
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=nonix_mini_artist
```

## 🔧 Troubleshooting

### **Common Startup Issues:**

**Python not found:**
```bash
# Check Python installation
python3 --version
# or
python --version

# Install Python 3.7+ if needed
sudo apt install python3 python3-pip  # Ubuntu/Debian
brew install python3                  # macOS
```

**Dependencies missing:**
```bash
# Install requirements
pip install -r requirements.txt

# Or install individually
pip install tkinter sqlite3 peewee nicegui
```

**Virtual environment issues:**
```bash
# Create new virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies in venv
pip install -r requirements.txt
```

**Permission denied on startup script:**
```bash
# Make script executable
chmod +x start.sh
```

### **Getting Help:**
- Check the terminal output for specific error messages
- Verify Python version (3.7+ required)
- Ensure all dependencies are installed
- Check if virtual environment is activated
- Look for missing configuration files

## 📖 Usage Examples

### **Reusable UI Layout**
```python
from nonix_mini_artist.ui.layout import MasterLayout
from nonix_mini_artist.ui.components import Sidebar, Header, ContentArea

# Master layout with reusable components
layout = MasterLayout()
layout.sidebar = Sidebar([
    {"title": "Artists", "icon": "🎤", "route": "/artists"},
    {"title": "Albums", "icon": "💿", "route": "/albums"},
    {"title": "Tracks", "icon": "🎵", "route": "/tracks"},
    {"title": "AI Settings", "icon": "🤖", "route": "/ai-settings"}
])
layout.header = Header(title="Music Manager", user_info=user)
layout.content = ContentArea()
```

### **Reusable UI Components**
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

### **Generic CRUD Helper (Backend)**
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

### **Service Layer (Using Generic CRUD)**
```python
from nonix_mini_artist.services.music_service import MusicService

# Create artist using generic CRUD
artist = await music_service.create_artist(
    name="The Rolling Calf",
    abbreviation="TRC",
    description="Dancehall legend from Jamaica"
)
```

### **UI Components Using Generic CRUD**
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

### **Google AI Analysis** 🤖
```python
from nonix_mini_artist.ai.service import AIService
from nonix_mini_artist.ai.models import AIAnalysisRequest

# Initialize AI service
ai_service = AIService()

# Analyze lyrics with Google AI
request = AIAnalysisRequest(
    preset_name="lyrics_analyzer",
    content="Your lyrics here...",
    context={"artist": "TRC", "genre": "dancehall"}
)

response = await ai_service.analyze(request)
print(f"AI Analysis: {response.content}")
```

### **Runtime AI Configuration** ⚡
```python
# All AI settings changeable via UI without restart!

# Add new Google AI provider
ai_service.add_provider({
    "name": "new_gemini",
    "api_key": "new_api_key",
    "enabled": True
})

# Create custom analysis preset
ai_service.add_preset(AIPreset(
    name="custom_analyzer",
    provider="gemini",
    model="gemini-1.5-pro",
    system_prompt="Your custom prompt...",
    temperature=0.5
))

# All changes take effect immediately!
```

## 🚀 **Runtime Management Features**

### **What You Can Change Without Restart:**
1. **API Keys**: Modify Google AI API keys instantly
2. **Provider Settings**: Add/edit/delete AI providers
3. **AI Presets**: Create custom analysis types
4. **System Prompts**: Modify AI behavior
5. **Model Selection**: Switch between AI models
6. **Temperature/Creativity**: Adjust AI response style
7. **Token Limits**: Control response length
8. **Provider Status**: Enable/disable services

### **UI Controls Available:**
- ➕ **Add Provider**: New Google AI services
- ✏️ **Edit Provider**: Change API keys, settings
- 🔍 **Test Provider**: Verify connections
- 🗑️ **Delete Provider**: Remove unused services
- 🔄 **Enable/Disable**: Turn providers on/off
- ➕ **Add Preset**: New analysis types
- ✏️ **Edit Preset**: Modify AI behavior
- 👁️ **View Preset**: See full configuration
- 🗑️ **Delete Preset**: Remove unused presets

### **Hot-Swapping Features:**
- ✅ **API key changes** take effect immediately
- ✅ **Provider switching** works instantly
- ✅ **Preset modifications** apply right away
- ✅ **Configuration updates** are live
- ✅ **Connection testing** happens in real-time
- ✅ **New providers** are instantly usable
- ✅ **New presets** are immediately available
- ✅ **Modified settings** apply to next analysis

## 🤝 Contributing

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
- **AI Features**: See `AI_FEATURES_README.md` for Google AI setup

## 🚀 **Ready to Start?**

### **Quick Launch Commands:**

**🎯 One-Command Startup:**
```bash
# Linux/macOS
./start.sh

# Windows
start.bat

# Any platform
python start.py
```

**🔧 Manual Launch:**
```bash
# Activate environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Run application
python main.py
# or
python src/nonix_mini_artist/ui/app.py
```

### **What Happens When You Start:**
1. 🎵 **Application loads** with modern UI
2. 🤖 **AI services initialize** (if configured)
3. 📊 **Database connects** to local SQLite
4. 🎨 **Interface appears** with sidebar navigation
5. 🚀 **Ready to manage** your music collection!

---

**Nonix Mini Artist Manager** - **Complete AI-powered music metadata management with FULL runtime control!** 🎵✨🤖⚡

**🚀 Status: ALL PHASES COMPLETED - FULLY FUNCTIONAL WITH GOOGLE AI INTEGRATION!**

**🎯 Get Started Now: `./start.sh` (Linux/Mac) or `start.bat` (Windows)**