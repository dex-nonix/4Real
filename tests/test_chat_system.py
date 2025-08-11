"""
Comprehensive tests for the chat system
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the modules to test
from src.nonix_mini_artist.core.database import init_database
from src.nonix_mini_artist.services.persona_service import AIPersonaService
from src.nonix_mini_artist.services.chat_service import ChatService
from src.nonix_mini_artist.services.tool_registry import ToolRegistry
from src.nonix_mini_artist.core.models import AIPersona, ChatSession, ChatMessage, Artist

class TestChatSystem:
    """Test suite for the chat system"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment"""
        # Initialize test database
        init_database()
        
        # Create test services
        self.persona_service = AIPersonaService()
        self.chat_service = ChatService()
        self.tool_registry = ToolRegistry()
        
        # Create test data
        await self._create_test_data()
        
        yield
        
        # Cleanup
        await self._cleanup_test_data()
    
    async def _create_test_data(self):
        """Create test data for testing"""
        # Create test artist
        self.test_artist = await self.persona_service.artist_crud.create(
            name="Test Artist",
            abbreviation="TA"
        )
        
        # Create test persona
        self.test_persona = await self.persona_service.create_persona(
            name="Test Persona",
            is_artist=True,
            artist_id=self.test_artist.id,
            system_prompt="You are a test persona for testing purposes.",
            personality_traits=["test", "reliable"],
            speaking_style="Professional and clear",
            knowledge_base="Testing and validation",
            tool_permissions=["read_file", "query_artist_data"]
        )
        
        # Create test chat session
        self.test_session = await self.chat_service.create_session(
            self.test_persona.id,
            "Test Chat Session"
        )
    
    async def _cleanup_test_data(self):
        """Clean up test data"""
        try:
            if hasattr(self, 'test_session'):
                await self.chat_service.delete_session(self.test_session.id)
            if hasattr(self, 'test_persona'):
                await self.persona_service.delete_persona(self.test_persona.id)
            if hasattr(self, 'test_artist'):
                await self.persona_service.artist_crud.delete(self.test_artist.id)
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_persona_creation(self):
        """Test persona creation functionality"""
        # Test basic persona creation
        persona = await self.persona_service.create_persona(
            name="Test Persona 2",
            is_artist=False,
            system_prompt="Test system prompt",
            tool_permissions=["read_file"]
        )
        
        assert persona.name == "Test Persona 2"
        assert persona.is_artist == False
        assert persona.system_prompt == "Test system prompt"
        
        # Cleanup
        await self.persona_service.delete_persona(persona.id)
    
    @pytest.mark.asyncio
    async def test_artist_persona_template(self):
        """Test artist persona template creation"""
        # Test dancehall template
        dancehall_persona = await self.persona_service.create_artist_persona_template(
            self.test_artist.id, 'dancehall'
        )
        
        assert dancehall_persona.is_artist == True
        assert dancehall_persona.artist_id == self.test_artist.id
        assert 'dancehall' in dancehall_persona.system_prompt.lower()
        assert 'jamaican' in dancehall_persona.knowledge_base.lower()
        
        # Cleanup
        await self.persona_service.delete_persona(dancehall_persona.id)
    
    @pytest.mark.asyncio
    async def test_chat_session_management(self):
        """Test chat session creation and management"""
        # Test session creation
        session = await self.chat_service.create_session(
            self.test_persona.id,
            "Test Session 2"
        )
        
        assert session.persona_id == self.test_persona.id
        assert session.title == "Test Session 2"
        assert session.is_active == True
        
        # Test session retrieval
        retrieved_session = await self.chat_service.get_session(session.id)
        assert retrieved_session.id == session.id
        assert retrieved_session.title == session.title
        
        # Test session deletion
        success = await self.chat_service.delete_session(session.id)
        assert success == True
    
    @pytest.mark.asyncio
    async def test_message_management(self):
        """Test chat message functionality"""
        # Test adding user message
        user_message = await self.chat_service.add_message(
            self.test_session.id,
            'user',
            'Hello, test message',
            'text'
        )
        
        assert user_message.sender_type == 'user'
        assert user_message.content == 'Hello, test message'
        assert user_message.message_type == 'text'
        
        # Test adding persona message
        persona_message = await self.chat_service.add_message(
            self.test_session.id,
            'persona',
            'Hello! How can I help you?',
            'text'
        )
        
        assert persona_message.sender_type == 'persona'
        assert persona_message.content == 'Hello! How can I help you?'
        
        # Test message retrieval
        messages = await self.chat_service.get_session_messages(self.test_session.id)
        assert len(messages) == 2
        
        # Test message history
        history = await self.chat_service.get_session_history(self.test_session.id)
        assert len(history) == 2
        assert history[0]['sender_type'] == 'user'
        assert history[1]['sender_type'] == 'persona'
    
    @pytest.mark.asyncio
    async def test_tool_registry(self):
        """Test tool registry functionality"""
        # Test available tools
        tools = self.tool_registry.get_available_tools()
        assert len(tools) > 0
        assert 'read_file' in tools
        
        # Test tool categories
        categories = self.tool_registry.get_tool_categories()
        assert len(categories) > 0
        assert 'file_operations' in categories
        
        # Test tool execution
        result = await self.tool_registry.execute_tool('read_file', file_path='test.txt')
        assert 'error' in result  # Should error for non-existent file
    
    @pytest.mark.asyncio
    async def test_artist_tools(self):
        """Test artist-specific tool functionality"""
        # Test artist-specific tools
        artist_tools = await self.persona_service.get_artist_specific_tools(self.test_persona.id)
        
        assert not artist_tools.get('error')
        assert artist_tools['total_available'] > 0
        assert 'enhanced_categories' in artist_tools
    
    @pytest.mark.asyncio
    async def test_content_access_validation(self):
        """Test artist content access validation"""
        # Test valid access
        has_access = await self.persona_service.validate_artist_content_access(
            self.test_persona.id, 'artist', self.test_artist.id
        )
        assert has_access == True
        
        # Test invalid access (different artist)
        other_artist = await self.persona_service.artist_crud.create(
            name="Other Artist",
            abbreviation="OA"
        )
        
        has_access = await self.persona_service.validate_artist_content_access(
            self.test_persona.id, 'artist', other_artist.id
        )
        assert has_access == False
        
        # Cleanup
        await self.persona_service.artist_crud.delete(other_artist.id)
    
    @pytest.mark.asyncio
    async def test_conversation_starters(self):
        """Test artist conversation starters"""
        starters = await self.persona_service.get_artist_conversation_starters(self.test_persona.id)
        assert len(starters) > 0
        assert any('test artist' in starter.lower() for starter in starters)
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        # Test invalid session ID
        with pytest.raises(ValueError):
            await self.chat_service.add_message(
                99999,  # Invalid session ID
                'user',
                'test message',
                'text'
            )
        
        # Test invalid persona ID
        with pytest.raises(ValueError):
            await self.persona_service.get_persona(99999)
        
        # Test tool execution with invalid tool
        result = await self.tool_registry.execute_tool('invalid_tool')
        assert result['success'] == False
        assert 'not found' in result['error']
    
    @pytest.mark.asyncio
    async def test_performance(self):
        """Test basic performance characteristics"""
        import time
        
        # Test persona creation performance
        start_time = time.time()
        persona = await self.persona_service.create_persona(
            name="Performance Test Persona",
            system_prompt="Test prompt",
            tool_permissions=["read_file"]
        )
        creation_time = time.time() - start_time
        
        assert creation_time < 1.0  # Should complete in under 1 second
        
        # Test message retrieval performance
        start_time = time.time()
        messages = await self.chat_service.get_session_messages(self.test_session.id)
        retrieval_time = time.time() - start_time
        
        assert retrieval_time < 0.5  # Should complete in under 0.5 seconds
        
        # Cleanup
        await self.persona_service.delete_persona(persona.id)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
