from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from .....database import AsyncSessionLocal
from ....service_router.decorators import expose
from .....models.chat_history import ChatHistory
from .....models.chat_message import ChatMessage
from .....models.chat_session import ChatSession
from .....models.persona import Persona


class ChatSessionMixin:
    """Mixin for chat session management operations."""

    async def _get_persona_by_id(self, db_session, persona_id: int):
        """Get persona by ID with validation."""
        persona_stmt = select(Persona).filter_by(id=persona_id, is_active=True)
        persona_result = await db_session.execute(persona_stmt)
        return persona_result.scalar_one_or_none()

    async def _get_session_by_id(self, db_session, session_id: int):
        """Get session by ID with validation."""
        session_stmt = select(ChatSession).filter_by(id=session_id, is_active=True)
        session_result = await db_session.execute(session_stmt)
        return session_result.scalar_one_or_none()

    async def _get_sessions_with_history_counts(self, persona_id: int = None, session_id: int = None):
        """Utility method to get sessions with history counts using single JOIN query."""

        async with AsyncSessionLocal() as db_session:
            # Build the query using select
            stmt = select(
                ChatSession,
                func.count(ChatHistory.id).label('history_count')
            ).outerjoin(
                ChatHistory, ChatSession.id == ChatHistory.session_id
            ).filter(
                ChatSession.is_active == True
            )

            if persona_id:
                stmt = stmt.filter(ChatSession.persona_id == persona_id)
            if session_id:
                stmt = stmt.filter(ChatSession.id == session_id)

            stmt = stmt.group_by(ChatSession.id)
            
            result = await db_session.execute(stmt)
            return result

    @expose(
        '/sessions',
        methods=['POST'],
        status_codes={201: 'Created', 400: 'Bad Request', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "persona_id": {"type": "integer", "description": "Persona ID"},
                "session_name": {"type": "string", "description": "Session name"},
                "session_icon": {"type": "string", "description": "Session icon"}
            },
            "required": ["persona_id"]
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def create_session(self, req: Request, payload: dict = None):
        """Create a new chat session."""
        async with AsyncSessionLocal() as db_session:
            try:
                payload = payload or {}
                persona_id = int(payload.get('persona_id'))
                
                # Get persona first to check if exists and get name
                persona = await self._get_persona_by_id(db_session, persona_id)
                if not persona:
                    return JSONResponse({'error': 'Persona not found or inactive'}, 404)
                
                session_name = payload.get('session_name') or f'Chat with {persona.name}'
                session_icon = payload.get('session_icon')

                session = ChatSession(
                    persona_id=persona_id,
                    session_name=session_name,
                    session_icon=session_icon,
                    is_active=True
                )
                db_session.add(session)
                await db_session.commit()
                await db_session.refresh(session)

                # Create initial history for the session
                history = ChatHistory(
                    session_id=session.id,
                    title='New Conversation',
                    message_count=0
                )
                db_session.add(history)
                await db_session.commit()
                await db_session.refresh(history)

                # Set this as the current history
                session.current_history_id = history.id
                await db_session.commit()

                # Optional initial system message from persona.system_prompt
                if persona.system_prompt:
                    sys_msg = ChatMessage(
                        history_id=history.id,
                        role='system',
                        message_type='text',
                        content_json={'type': 'system', 'text': persona.system_prompt}
                    )
                    db_session.add(sys_msg)
                    await db_session.commit()

                return JSONResponse({'data': session.to_dict()})
            except Exception as exc: 
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, status_code=500)

    @expose(
        '/sessions',
        methods=['GET'],
        status_codes={200: 'OK'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "persona_id": {"type": "integer"},
                            "session_name": {"type": "string"},
                            "session_icon": {"type": "string"},
                            "is_active": {"type": "boolean"},
                            "current_history_id": {"type": "integer"},
                            "history_count": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
    async def list_sessions(self, req: Request):
        """List all active chat sessions."""
        try:
            # Use utility method for single JOIN query with COUNT
            sessions_result = await self._get_sessions_with_history_counts()
            sessions_with_counts = sessions_result.all()

            result = []
            for session, history_count in sessions_with_counts:
                session_data = session.to_dict()
                session_data['history_count'] = history_count  # Just the count, no objects
                result.append(session_data)
            return JSONResponse({'data': result, 'total': len(result)})
        except Exception as exc: 
            return JSONResponse({'error': str(exc)}, 500)

    @expose(
        '/sessions/{id}',
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "history_count": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def get_session(self, req: Request, id: int):
        """Get a specific chat session by ID."""
        try:
            # Use utility method for single JOIN query with COUNT
            sessions_result = await self._get_sessions_with_history_counts(session_id=id)
            session_with_count = sessions_result.first()

            if not session_with_count:
                return JSONResponse({'error': 'Session not found or inactive'}, 404)

            session, history_count = session_with_count
            session_data = session.to_dict()
            session_data['history_count'] = history_count  # Just the count, no objects

            return JSONResponse({'data': session_data})
        except Exception as exc: 
            return JSONResponse({'error': str(exc)}, 500)

    @expose(
        '/sessions/{id}',
        methods=['PUT'],
        status_codes={200: 'OK', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "session_name": {"type": "string", "description": "Session name"},
                "session_icon": {"type": "string", "description": "Session icon"},
                "current_history_id": {"type": "integer", "description": "Current history ID"}
            }
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def update_session(self, req: Request, payload: dict = None, id: int = None):
        """Update a chat session."""
        async with AsyncSessionLocal() as db_session:
            try:
                session = await self._get_session_by_id(db_session, id)
                if not session:
                    return JSONResponse({'error': 'Session not found or inactive'}, 404)

                data = payload or {}
                allowed_fields = ['session_name', 'session_icon', 'current_history_id']

                for field in allowed_fields:
                    if field in data:
                        setattr(session, field, data[field])

                await db_session.commit()
                return JSONResponse({'data': session.to_dict()})
            except Exception as exc:
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, 500)

    @expose(
        '/sessions/{id}',
        methods=['DELETE'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    )
    async def delete_session(self, req: Request, id: int):
        """Delete a chat session (soft delete by setting is_active=False)."""
        async with AsyncSessionLocal() as db_session:
            try:
                session = await self._get_session_by_id(db_session, id)
                if not session:
                    return JSONResponse({'error': 'Session not found or inactive'}, 404)

                session.is_active = False
                await db_session.commit()
                return JSONResponse({'message': 'Session deleted successfully'})
            except Exception as exc:
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, 500)

    @expose(
        '/personas/{persona_id}/sessions',
        methods=['GET'],
        status_codes={200: 'OK', 404: 'Not Found'},
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "persona_id": {"type": "integer"},
                            "session_name": {"type": "string"},
                            "session_icon": {"type": "string"},
                            "is_active": {"type": "boolean"},
                            "current_history_id": {"type": "integer"},
                            "history_count": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                },
                "total": {"type": "integer"}
            }
        }
    )
    async def get_persona_sessions(self, req: Request, persona_id: int):
        """Get all sessions for a specific persona."""
        async with AsyncSessionLocal() as db_session:
            try:
                persona = await self._get_persona_by_id(db_session, persona_id)
                if not persona:
                    return JSONResponse({'error': 'Persona not found or inactive'}, 404)

                # Use utility method for single JOIN query with COUNT
                sessions_result = await self._get_sessions_with_history_counts(persona_id=persona_id)
                sessions_with_counts = sessions_result.all()

                sessions_data = []
                for session, history_count in sessions_with_counts:
                    session_data = session.to_dict()
                    session_data['history_count'] = history_count  # Just the count, no objects
                    sessions_data.append(session_data)

                return JSONResponse({'data': sessions_data, 'total': len(sessions_data)})
            except Exception as exc:
                return JSONResponse({'error': str(exc)}, 500)

    @expose(
        '/personas/{persona_id}/start-chat',
        methods=['POST'],
        status_codes={201: 'Created', 404: 'Not Found'},
        request_schema={
            "type": "object",
            "properties": {
                "session_name": {"type": "string", "description": "Session name"},
                "session_icon": {"type": "string", "description": "Session icon"}
            }
        },
        response_schema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "persona_id": {"type": "integer"},
                        "session_name": {"type": "string"},
                        "session_icon": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "current_history_id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    )
    async def start_chat_with_persona(self, req: Request, payload: dict = None, persona_id: int = None):
        """Start a new chat session with a persona."""
        async with AsyncSessionLocal() as db_session:
            try:
                persona = await self._get_persona_by_id(db_session, persona_id)
                if not persona:
                    return JSONResponse({'error': 'Persona not found or inactive'}, 404)

                payload = payload or {}
                session_name = payload.get('session_name') or f'Chat with {persona.name}'
                session_icon = payload.get('session_icon')

                # Create new session
                session = ChatSession(
                    persona_id=persona_id,
                    session_name=session_name,
                    session_icon=session_icon,
                    is_active=True
                )
                db_session.add(session)
                await db_session.commit()
                await db_session.refresh(session)

                # Create initial history
                history = ChatHistory(
                    session_id=session.id,
                    title='New Conversation',
                    message_count=0
                )
                db_session.add(history)
                await db_session.commit()
                await db_session.refresh(history)

                # Set as current history
                session.current_history_id = history.id
                await db_session.commit()

                # Add system message if persona has one
                if persona.system_prompt:
                    sys_msg = ChatMessage(
                        history_id=history.id,
                        role='system',
                        message_type='text',
                        content_json={'type': 'system', 'text': persona.system_prompt}
                    )
                    db_session.add(sys_msg)
                    await db_session.commit()

                return JSONResponse({'data': session.to_dict()}, 201)
            except Exception as exc:
                await db_session.rollback()
                return JSONResponse({'error': str(exc)}, 500)
