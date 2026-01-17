# Conversation Memory Guide

This document explains how conversation memory works for handling follow-up questions.

## Overview

The system maintains conversation history to provide context for follow-up questions. This allows students to ask questions like:

- "What are the enrolment requirements?" (initial question)
- "Do I need insurance?" (follow-up, referring to enrolment)
- "How much does it cost?" (follow-up, needs context)

## How It Works

### Conversation Flow

1. **First Question**: Student asks a question
   - System creates a new `conversation_id`
   - Stores the question
   - Generates response
   - Stores the response
   - Returns `conversation_id` to client

2. **Follow-up Questions**: Student asks follow-up
   - Client sends `conversation_id` with the question
   - System retrieves conversation history
   - Includes history in the prompt context
   - Generates contextualized response
   - Updates conversation history

### Memory Storage

- **Storage**: In-memory (default) - fast but lost on restart
- **TTL**: 24 hours (configurable)
- **Max History**: 10 messages per conversation (configurable)
- **Auto-cleanup**: Expired conversations are automatically cleared

## Configuration

### Environment Variables

```env
# Enable/disable conversation memory
ENABLE_CONVERSATION_MEMORY=true

# Maximum number of previous messages to keep
MAX_CONVERSATION_HISTORY=10

# Time to live for conversations (hours)
CONVERSATION_TTL_HOURS=24
```

## API Usage

### Initial Question

```json
POST /api/v1/query
{
  "query": "What are the enrolment requirements?",
  "student_id": "student123"
}
```

**Response**:
```json
{
  "response": "To enroll in ICL Graduate Business Programmes...",
  "conversation_id": "abc-123-def-456",
  "language": "en",
  "confidence": 0.95,
  "sources": ["chunk_1", "chunk_2"]
}
```

### Follow-up Question

```json
POST /api/v1/query
{
  "query": "Do I need insurance?",
  "student_id": "student123",
  "conversation_id": "abc-123-def-456"
}
```

The system will:
1. Retrieve previous conversation history
2. Include it in the context
3. Generate a response that understands the follow-up
4. Update conversation history

## Example Conversation

**Student**: "What are the enrolment requirements?"

**System**: "To enroll in ICL Graduate Business Programmes, both domestic and international students are required to: Have a valid visa to study in New Zealand (international students), Have suitable travel/medical insurance, Have enough funds for onward travel..."

**Student**: "Do I need insurance?" (follow-up)

**System**: "Yes, as mentioned in the enrolment requirements, you need suitable travel/medical insurance. Your insurance should cover the time that you are studying in, and the travel time to and from New Zealand. If you don't have appropriate medical insurance, our Marketing team will be able to assist you..."

## Memory Management

### Automatic Cleanup

- Conversations older than TTL are automatically cleared
- Memory is checked periodically
- No manual intervention needed

### Manual Cleanup

```python
from app.services.conversation_memory import get_conversation_memory

memory = get_conversation_memory()
memory.clear_conversation(conversation_id)
memory.clear_expired()  # Clear all expired
```

## Memory Limits

### Per Conversation
- **Max Messages**: 10 (configurable)
- **Oldest messages**: Automatically removed when limit reached
- **Keeps**: Most recent messages

### System-Wide
- **No hard limit**: Limited by available memory
- **TTL**: 24 hours default
- **Auto-cleanup**: Prevents memory bloat

## Context Inclusion

When a follow-up question is asked, the system includes:

1. **Previous conversation** (last N messages)
2. **Current query**
3. **Retrieved documents** from vector search
4. **All combined** in the prompt

This ensures the AI understands:
- What was discussed before
- What the current question refers to
- Relevant information from the knowledge base

## Best Practices

### For Clients (n8n, etc.)

1. **Store conversation_id**: Save it after the first response
2. **Include in follow-ups**: Always send conversation_id with subsequent questions
3. **Handle new conversations**: If conversation_id is missing, create a new one
4. **Timeout handling**: If conversation expired, start a new one

### For Configuration

1. **Adjust TTL**: Based on your use case
   - Short sessions: 1-2 hours
   - Long sessions: 24-48 hours
2. **History size**: Balance context vs. prompt size
   - More history = better context but larger prompts
   - Recommended: 5-10 messages
3. **Enable/disable**: Turn off if not needed to save memory

## Limitations

1. **In-memory only**: Lost on server restart
   - For production, consider persistent storage
2. **No cross-student memory**: Each conversation is isolated
3. **No long-term memory**: Only recent conversation history
4. **Language**: Memory works best when conversation is in same language

## Future Enhancements

Potential improvements:
- Persistent storage (database)
- Cross-conversation learning
- Long-term memory for frequent students
- Conversation summarization
- Multi-language support in memory

## Troubleshooting

### Memory Not Working

1. Check `ENABLE_CONVERSATION_MEMORY=true` in `.env`
2. Verify `conversation_id` is being sent
3. Check logs for memory operations
4. Ensure conversation hasn't expired

### Context Not Preserved

1. Increase `MAX_CONVERSATION_HISTORY`
2. Check if conversation_id is correct
3. Verify memory is enabled
4. Check TTL hasn't expired

### Memory Growing Too Large

1. Reduce `CONVERSATION_TTL_HOURS`
2. Reduce `MAX_CONVERSATION_HISTORY`
3. Enable auto-cleanup (default)
4. Manually clear expired conversations
