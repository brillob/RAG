# Swagger UI Testing Guide

Complete guide for using Swagger UI to test the RAG Student Support API locally.

## Accessing Swagger UI

### Start the Server

```bash
# Make sure you've processed the handbook first
python scripts/process_handbook.py

# Start the server
python -m app.main
```

### Open Swagger UI

Once the server is running, open your browser and navigate to:

**Swagger UI**: http://localhost:8000/docs

**Alternative Documentation**:
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Swagger UI Features

### 1. Interactive API Testing

Swagger UI provides an interactive interface where you can:
- ✅ Test all endpoints directly from the browser
- ✅ See request/response schemas
- ✅ View example requests and responses
- ✅ Try different parameters
- ✅ See authentication requirements

### 2. Endpoint Documentation

Each endpoint includes:
- **Description**: What the endpoint does
- **Parameters**: Required and optional fields
- **Request Body**: Example JSON
- **Responses**: Example responses for different status codes
- **Try it out**: Interactive testing button

## Testing the Query Endpoint

### Step 1: Expand the Query Endpoint

1. Find the **"Student Queries"** section
2. Click on **POST /api/v1/query**
3. Click **"Try it out"** button

### Step 2: Fill in the Request

Example request body:

```json
{
  "query": "What are the enrolment requirements?",
  "student_id": "student123",
  "language": "auto",
  "conversation_id": null
}
```

**Fields**:
- `query` (required): The student's question
- `student_id` (optional): Student identifier
- `language` (optional): Language code or "auto" for detection
- `conversation_id` (optional): For follow-up questions

### Step 3: Execute

1. Click **"Execute"** button
2. Wait for the response
3. View the response

### Step 4: Test Follow-up Question

1. Copy the `conversation_id` from the response
2. Create a new request with:
```json
{
  "query": "Do I need insurance?",
  "conversation_id": "paste-conversation-id-here"
}
```
3. Execute to see how conversation context is used

## Example Test Scenarios

### Scenario 1: Basic Query

```json
{
  "query": "What are the enrolment requirements?"
}
```

**Expected**: Response about enrolment requirements with high confidence.

### Scenario 2: Multilingual Query

```json
{
  "query": "¿Cuáles son los requisitos de admisión?",
  "language": "auto"
}
```

**Expected**: Response in Spanish (or detected language).

### Scenario 3: Follow-up Question

```json
// First question
{
  "query": "What documents do I need for enrolment?"
}

// Follow-up (use conversation_id from first response)
{
  "query": "What about insurance?",
  "conversation_id": "from-previous-response"
}
```

**Expected**: Second response understands context from first question.

### Scenario 4: Specific Language

```json
{
  "query": "What are the visa requirements?",
  "language": "en"
}
```

**Expected**: Response in English (forced).

### Scenario 5: Query with No Results

```json
{
  "query": "What is the weather today?"
}
```

**Expected**: Response indicating insufficient information.

## Authentication

### If API Key is Configured

1. Click **"Authorize"** button at the top
2. Enter your API key
3. Click **"Authorize"**
4. All requests will include the API key automatically

### If No API Key

If `API_KEY` is not set in `.env`, authentication is disabled and you can test without authorization.

## Response Fields Explained

### Successful Response (200)

```json
{
  "response": "The answer to the question...",
  "language": "en",
  "confidence": 0.95,
  "sources": ["chunk_1", "chunk_2"],
  "query_id": "unique-query-id",
  "conversation_id": "conversation-id-for-follow-ups"
}
```

- **response**: The AI-generated answer
- **language**: Detected/used language code
- **confidence**: How confident the system is (0.0 to 1.0)
- **sources**: Document chunks used
- **query_id**: Unique identifier for this query
- **conversation_id**: Use this for follow-up questions

### Error Responses

- **401 Unauthorized**: Invalid or missing API key
- **422 Validation Error**: Invalid request format
- **500 Internal Server Error**: Server-side error

## Tips for Testing

### 1. Test Different Query Types

- Enrolment questions
- Visa questions
- Support questions
- Accommodation questions
- Financial questions

### 2. Test Conversation Flow

1. Ask initial question
2. Copy `conversation_id`
3. Ask follow-up using the same `conversation_id`
4. Verify context is maintained

### 3. Test Language Detection

- English queries
- Spanish queries
- Other supported languages
- Mixed language queries

### 4. Test Edge Cases

- Very short queries
- Very long queries
- Queries with no results
- Empty or invalid requests

## Swagger UI Features

### Request/Response Examples

Each endpoint shows:
- Example request body
- Example responses for different status codes
- Schema definitions

### Schema Inspection

Click on any model to see:
- Field descriptions
- Data types
- Required vs optional fields
- Example values

### Download/Import

- **Download**: Export OpenAPI spec
- **Import**: Import OpenAPI spec for testing

## Troubleshooting

### Swagger UI Not Loading

1. Check server is running: `python -m app.main`
2. Check port: Default is 8000
3. Check URL: http://localhost:8000/docs

### "Try it out" Not Working

1. Make sure you clicked "Try it out" button
2. Fill in required fields
3. Check for validation errors (red text)

### Authentication Errors

1. Check if API key is required (check `.env`)
2. Use "Authorize" button to set API key
3. Or disable API key in `.env` for testing

### No Response/Timeout

1. Check server logs for errors
2. Verify vector database is populated
3. Check if handbook was processed

## Alternative: ReDoc

ReDoc provides an alternative documentation view:

**URL**: http://localhost:8000/redoc

**Features**:
- Clean, readable layout
- Better for documentation reading
- Less interactive than Swagger UI

## API Testing Workflow

### Recommended Testing Order

1. **Health Check**: Verify server is running
   ```
   GET /health
   ```

2. **Root Endpoint**: Get API information
   ```
   GET /
   ```

3. **First Query**: Test basic functionality
   ```
   POST /api/v1/query
   {
     "query": "What are the enrolment requirements?"
   }
   ```

4. **Follow-up Query**: Test conversation memory
   ```
   POST /api/v1/query
   {
     "query": "Do I need insurance?",
     "conversation_id": "from-step-3"
   }
   ```

5. **Multilingual Query**: Test language detection
   ```
   POST /api/v1/query
   {
     "query": "¿Cuáles son los requisitos?",
     "language": "auto"
   }
   ```

## Integration with n8n

Swagger UI helps you:
- Understand the API structure
- Test requests before integrating
- See example responses
- Debug integration issues

Use the examples from Swagger UI when configuring n8n HTTP Request nodes.

## Next Steps

After testing in Swagger UI:
1. Integrate with n8n using the tested requests
2. Deploy to production
3. Monitor API usage
4. Iterate based on feedback
