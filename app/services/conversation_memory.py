"""Conversation memory management for handling follow-up questions."""
import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history for context in follow-up questions."""
    
    def __init__(self, max_history: int = 10, ttl_hours: int = 24):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of previous messages to keep per conversation
            ttl_hours: Time to live for conversations in hours
        """
        self.max_history = max_history
        self.ttl_hours = ttl_hours
        # In-memory storage: conversation_id -> list of messages
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)
        # Track conversation creation time
        self.conversation_times: Dict[str, datetime] = {}
        logger.info(f"Conversation memory initialized (max_history={max_history}, ttl={ttl_hours}h)")
    
    def create_conversation(self, student_id: Optional[str] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            student_id: Optional student identifier
            
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        self.conversation_times[conversation_id] = datetime.now()
        self.conversations[conversation_id] = []
        logger.debug(f"Created conversation {conversation_id} for student {student_id}")
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a message to conversation history.
        
        Args:
            conversation_id: Conversation ID
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (e.g., sources, confidence)
        """
        if conversation_id not in self.conversations:
            # Auto-create conversation if it doesn't exist
            self.create_conversation()
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.conversations[conversation_id].append(message)
        
        # Limit history size
        if len(self.conversations[conversation_id]) > self.max_history * 2:
            # Keep only the most recent messages
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history * 2:]
        
        logger.debug(f"Added {role} message to conversation {conversation_id}")
    
    def get_history(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation ID
            max_messages: Maximum number of messages to return (defaults to max_history)
            
        Returns:
            List of messages in chronological order
        """
        if conversation_id not in self.conversations:
            return []
        
        # Check TTL
        if self._is_expired(conversation_id):
            logger.debug(f"Conversation {conversation_id} expired, clearing")
            self.clear_conversation(conversation_id)
            return []
        
        history = self.conversations[conversation_id]
        
        if max_messages:
            return history[-max_messages:]
        
        return history[-self.max_history:]
    
    def get_context_string(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> str:
        """
        Get conversation history as a formatted string for prompt context.
        
        Args:
            conversation_id: Conversation ID
            max_messages: Maximum number of messages to include
            
        Returns:
            Formatted conversation context string
        """
        history = self.get_history(conversation_id, max_messages)
        
        if not history:
            return ""
        
        context_parts = ["Previous conversation:"]
        for msg in history:
            role_label = "Student" if msg['role'] == 'user' else "Assistant"
            context_parts.append(f"{role_label}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        if conversation_id in self.conversation_times:
            del self.conversation_times[conversation_id]
        logger.debug(f"Cleared conversation {conversation_id}")
    
    def clear_expired(self):
        """Clear all expired conversations."""
        expired = [
            conv_id for conv_id in self.conversation_times.keys()
            if self._is_expired(conv_id)
        ]
        for conv_id in expired:
            self.clear_conversation(conv_id)
        if expired:
            logger.info(f"Cleared {len(expired)} expired conversations")
    
    def _is_expired(self, conversation_id: str) -> bool:
        """Check if a conversation has expired."""
        if conversation_id not in self.conversation_times:
            return True
        
        age = datetime.now() - self.conversation_times[conversation_id]
        return age > timedelta(hours=self.ttl_hours)
    
    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """Get summary of a conversation."""
        history = self.get_history(conversation_id)
        return {
            'conversation_id': conversation_id,
            'message_count': len(history),
            'created_at': self.conversation_times.get(conversation_id, datetime.now()).isoformat(),
            'last_message': history[-1]['timestamp'] if history else None
        }


# Global instance
_conversation_memory: Optional[ConversationMemory] = None


def get_conversation_memory() -> ConversationMemory:
    """Get or create the global conversation memory instance."""
    global _conversation_memory
    if _conversation_memory is None:
        from app.config import settings
        _conversation_memory = ConversationMemory(
            max_history=settings.max_conversation_history,
            ttl_hours=settings.conversation_ttl_hours
        )
    return _conversation_memory
