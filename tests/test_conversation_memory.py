"""Unit tests for conversation memory."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.services.conversation_memory import ConversationMemory, get_conversation_memory


@pytest.fixture
def memory():
    """Create conversation memory instance."""
    return ConversationMemory(max_history=5, ttl_hours=1)


def test_create_conversation(memory):
    """Test creating a new conversation."""
    conv_id = memory.create_conversation("student123")
    
    assert conv_id is not None
    assert len(conv_id) > 0
    assert conv_id in memory.conversations
    assert conv_id in memory.conversation_times


def test_create_conversation_without_student_id(memory):
    """Test creating conversation without student_id."""
    conv_id = memory.create_conversation()
    
    assert conv_id is not None
    assert conv_id in memory.conversations


def test_add_message(memory):
    """Test adding messages to conversation."""
    conv_id = memory.create_conversation()
    
    memory.add_message(conv_id, "user", "Hello")
    memory.add_message(conv_id, "assistant", "Hi there")
    
    history = memory.get_history(conv_id)
    assert len(history) == 2
    assert history[0]['role'] == 'user'
    assert history[0]['content'] == 'Hello'
    assert history[1]['role'] == 'assistant'
    assert history[1]['content'] == 'Hi there'


def test_add_message_with_metadata(memory):
    """Test adding message with metadata."""
    conv_id = memory.create_conversation()
    
    metadata = {'confidence': 0.95, 'sources': ['doc1']}
    memory.add_message(conv_id, "assistant", "Response", metadata)
    
    history = memory.get_history(conv_id)
    assert history[0]['metadata'] == metadata


def test_add_message_auto_create_conversation(memory):
    """Test that adding message auto-creates conversation if it doesn't exist."""
    conv_id = "new-conv-id"
    
    memory.add_message(conv_id, "user", "Hello")
    
    assert conv_id in memory.conversations
    assert len(memory.conversations[conv_id]) == 1


def test_get_history(memory):
    """Test retrieving conversation history."""
    conv_id = memory.create_conversation()
    
    for i in range(3):
        memory.add_message(conv_id, "user", f"Message {i}")
        memory.add_message(conv_id, "assistant", f"Response {i}")
    
    history = memory.get_history(conv_id)
    
    assert len(history) == 6
    assert all('timestamp' in msg for msg in history)


def test_get_history_max_messages(memory):
    """Test history retrieval with max_messages limit."""
    conv_id = memory.create_conversation()
    
    # Add more messages than max_history
    for i in range(10):
        memory.add_message(conv_id, "user", f"Message {i}")
    
    history = memory.get_history(conv_id, max_messages=3)
    
    assert len(history) == 3
    # Should get the most recent messages
    assert history[-1]['content'] == "Message 9"


def test_get_history_empty_conversation(memory):
    """Test getting history for empty conversation."""
    conv_id = memory.create_conversation()
    
    history = memory.get_history(conv_id)
    
    assert len(history) == 0


def test_get_history_nonexistent_conversation(memory):
    """Test getting history for non-existent conversation."""
    history = memory.get_history("nonexistent-id")
    
    assert len(history) == 0


def test_get_context_string(memory):
    """Test getting formatted context string."""
    conv_id = memory.create_conversation()
    
    memory.add_message(conv_id, "user", "What are the requirements?")
    memory.add_message(conv_id, "assistant", "You need a visa and insurance.")
    
    context = memory.get_context_string(conv_id)
    
    assert "Previous conversation" in context
    assert "Student:" in context
    assert "Assistant:" in context
    assert "requirements" in context
    assert "visa" in context


def test_get_context_string_empty(memory):
    """Test getting context string for empty conversation."""
    conv_id = memory.create_conversation()
    
    context = memory.get_context_string(conv_id)
    
    assert context == ""


def test_history_limit_enforcement(memory):
    """Test that history is limited to max_history."""
    conv_id = memory.create_conversation()
    
    # Add more than max_history * 2 to trigger trimming
    for i in range(15):
        memory.add_message(conv_id, "user", f"Message {i}")
    
    # Should be trimmed
    assert len(memory.conversations[conv_id]) <= 10  # max_history * 2


def test_clear_conversation(memory):
    """Test clearing a conversation."""
    conv_id = memory.create_conversation()
    memory.add_message(conv_id, "user", "Hello")
    
    memory.clear_conversation(conv_id)
    
    assert conv_id not in memory.conversations
    assert conv_id not in memory.conversation_times


def test_clear_expired(memory):
    """Test clearing expired conversations."""
    conv_id1 = memory.create_conversation()
    conv_id2 = memory.create_conversation()
    
    # Manually set old time for first conversation
    memory.conversation_times[conv_id1] = datetime.now() - timedelta(hours=2)
    
    memory.clear_expired()
    
    assert conv_id1 not in memory.conversations
    assert conv_id2 in memory.conversations  # Still valid


def test_is_expired(memory):
    """Test checking if conversation is expired."""
    conv_id = memory.create_conversation()
    
    # Set old time
    memory.conversation_times[conv_id] = datetime.now() - timedelta(hours=2)
    
    assert memory._is_expired(conv_id) is True


def test_is_expired_not_expired(memory):
    """Test that recent conversation is not expired."""
    conv_id = memory.create_conversation()
    
    assert memory._is_expired(conv_id) is False


def test_get_history_expired_conversation(memory):
    """Test getting history for expired conversation."""
    conv_id = memory.create_conversation()
    memory.add_message(conv_id, "user", "Hello")
    
    # Expire the conversation
    memory.conversation_times[conv_id] = datetime.now() - timedelta(hours=2)
    
    history = memory.get_history(conv_id)
    
    # Should return empty and clear the conversation
    assert len(history) == 0
    assert conv_id not in memory.conversations


def test_get_conversation_summary(memory):
    """Test getting conversation summary."""
    conv_id = memory.create_conversation("student123")
    memory.add_message(conv_id, "user", "Hello")
    memory.add_message(conv_id, "assistant", "Hi")
    
    summary = memory.get_conversation_summary(conv_id)
    
    assert summary['conversation_id'] == conv_id
    assert summary['message_count'] == 2
    assert 'created_at' in summary
    assert 'last_message' in summary


def test_get_conversation_memory_singleton():
    """Test that get_conversation_memory returns singleton."""
    with patch('app.services.conversation_memory._conversation_memory', None):
        with patch('app.config.settings') as mock_settings:
            mock_settings.max_conversation_history = 10
            mock_settings.conversation_ttl_hours = 24
            
            memory1 = get_conversation_memory()
            memory2 = get_conversation_memory()
            
            # Should be the same instance
            assert memory1 is memory2
