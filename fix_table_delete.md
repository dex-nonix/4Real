# Cascade Delete Implementation Tracker

## Models Needing Cascade Updates

### Music Artist Module
- [x] **album.py** - `albums` backref (Artist → Albums)
- [x] **track.py** - `tracks` backref (Album → Tracks)

### Agentic Module
- [x] **persona.py** - `personas` backref (Artist → Personas)
- [x] **persona.py** - `personas` backref (AIModelMapping → Personas)
- [x] **chat_session.py** - `chat_sessions` backref (Persona → ChatSessions)
- [x] **chat_session.py** - `current_sessions` backref (ChatHistory → ChatSessions)
- [x] **chat_history.py** - `histories` backref (ChatSession → ChatHistories)
- [x] **chat_message.py** - `messages` backref (ChatHistory → ChatMessages)
- [x] **ai_model_mapping.py** - `model_mappings` backref (AIProvider → AIModelMappings)
- [x] **chat_prompt.py** - `chat_prompts` backref (Template → ChatPrompts)

### File Manager Module
- [x] **file.py** - `files` backref (FileCategory → Files)

## Cascade Delete Hierarchy

```
Artist (deleted)
├── Albums
│   └── Tracks
│       └── AIAnalysisResults
├── Personas
│   ├── ChatSessions
│   │   └── ChatHistories
│   │       └── ChatMessages
│   │           └── ToolInvocationLogs
│   ├── PersonaMCPServers
│   └── PersonaToolAccess
└── AIAnalysisResults (via AIProvider)

Album (deleted)
└── Tracks
    └── AIAnalysisResults

Persona (deleted)
├── ChatSessions
│   └── ChatHistories
│       └── ChatMessages
│           └── ToolInvocationLogs
├── PersonaMCPServers
└── PersonaToolAccess

ChatSession (deleted)
└── ChatHistories
    └── ChatMessages
        └── ToolInvocationLogs

ChatHistory (deleted)
├── ChatMessages
│   └── ToolInvocationLogs
└── ToolInvocationLogs

ChatMessage (deleted)
└── ToolInvocationLogs

AIProvider (deleted)
├── AIModelMappings
│   └── Personas (cascade continues...)
└── AIAnalysisResults

AIModelMapping (deleted)
└── Personas (cascade continues...)

FileCategory (deleted)
└── Files
```

## Implementation Pattern

For each relationship, add `cascade='all, delete-orphan'` to the backref:

```python
backref=backref('relationship_name', lazy=True, cascade='all, delete-orphan')
```

## Many-to-Many Relationships

These cascade automatically when parent relationships are properly configured:
- `track_styles` (Track ↔ Style)
- `track_rhyme_techniques` (Track ↔ RhymeTechnique)
