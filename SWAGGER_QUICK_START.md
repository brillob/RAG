# Swagger UI - Quick Start Guide

Step-by-step guide to run and test the API using Swagger UI locally.

## 🚀 Step-by-Step Instructions

### Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10+ installed
- ✅ Dependencies installed: `pip install -r requirements.txt`
- ✅ Handbook processed (vector database populated)

### Step 1: Process the Handbook

First, you need to populate the vector database with the ICL Student Handbook:

```bash
python scripts/process_handbook.py
```

**Expected Output:**
```
🚀 Processing ICL Student Support Services Handbook...
✓ Extracted text from PDF
✓ Created X text chunks using sentence strategy
✓ Added X documents to vector database
✓ Processing complete!
```

**Troubleshooting:**
- If PDF download fails, check internet connection
- If processing fails, ensure `pdfplumber` is installed: `pip install pdfplumber`
- The script will download the PDF automatically from ICL's website

### Step 2: Start the Server

Start the FastAPI server:

```bash
python -m app.main
```

**Expected Output:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Loaded existing collection 'student_handbook' with X documents
INFO:     RAG Service initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Troubleshooting:**
- **Port already in use**: Change port in `.env`: `PORT=8001`
- **Import errors**: Run `pip install -r requirements.txt`
- **Vector DB empty**: Run Step 1 first

### Step 3: Open Swagger UI

Open your web browser and navigate to:

**http://localhost:8000/docs**

You should see the Swagger UI interface with:
- API title and description
- List of available endpoints
- Interactive testing interface

**Alternative Documentation:**
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Step 4: Test Health Endpoint

1. Find **GET /health** in the Swagger UI
2. Click on it to expand
3. Click **"Try it out"** button
4. Click **"Execute"** button
5. View the response:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0"
   }
   ```

✅ **Success**: If you see `"status": "healthy"`, the server is working!

### Step 5: Test Query Endpoint

1. Find **POST /api/v1/query** in the "Student Queries" section
2. Click on it to expand
3. Click **"Try it out"** button
4. The request body editor will appear
5. Replace the example with:
   ```json
   {
     "query": "What are the enrolment requirements?"
   }
   ```
6. Click **"Execute"** button
7. Scroll down to see the response

**Expected Response:**
```json
{
  "response": "To enroll in ICL Graduate Business Programmes...",
  "language": "en",
  "confidence": 0.95,
  "sources": ["chunk_1", "chunk_2"],
  "query_id": "unique-id",
  "conversation_id": "conversation-id"
}
```

✅ **Success**: If you see a response with information about enrolment, it's working!

### Step 6: Test Follow-up Question

1. Copy the `conversation_id` from the previous response
2. Create a new request in Swagger UI:
   ```json
   {
     "query": "Do I need insurance?",
     "conversation_id": "paste-conversation-id-here"
   }
   ```
3. Click **"Execute"**
4. The response should understand the context from the first question

✅ **Success**: If the response mentions insurance in the context of enrolment, conversation memory is working!

## 📋 Complete Test Scenarios

### Scenario 1: Basic Enrolment Query

**Request:**
```json
{
  "query": "What are the enrolment requirements?",
  "language": "auto"
}
```

**Expected**: Response about enrolment requirements with high confidence.

---

### Scenario 2: Visa Information

**Request:**
```json
{
  "query": "What visa do I need to study at ICL?",
  "student_id": "student123"
}
```

**Expected**: Response about visa requirements for international students.

---

### Scenario 3: Multilingual Query

**Request:**
```json
{
  "query": "¿Cuáles son los requisitos de admisión?",
  "language": "auto"
}
```

**Expected**: Response in Spanish (or detected language).

---

### Scenario 4: Follow-up Question

**First Request:**
```json
{
  "query": "What documents do I need for enrolment?"
}
```

**Copy `conversation_id` from response, then:**

**Follow-up Request:**
```json
{
  "query": "What about insurance?",
  "conversation_id": "from-previous-response"
}
```

**Expected**: Second response understands "insurance" refers to enrolment insurance.

---

### Scenario 5: Student Support Contact

**Request:**
```json
{
  "query": "How do I contact student support?",
  "language": "en"
}
```

**Expected**: Response with contact information from handbook.

---

### Scenario 6: Query with No Results

**Request:**
```json
{
  "query": "What is the weather today?"
}
```

**Expected**: Response indicating insufficient information (low confidence).

## 🔐 Authentication (If Required)

If you've set `API_KEY` in your `.env` file:

1. Click the **"Authorize"** button at the top of Swagger UI
2. Enter your API key
3. Click **"Authorize"**
4. Click **"Close"**
5. All requests will now include the API key automatically

**Note**: If `API_KEY` is not set, authentication is disabled for local testing.

## 🎯 Swagger UI Features

### Interactive Testing
- **"Try it out"**: Makes endpoints editable
- **Request Body Editor**: JSON editor with syntax highlighting
- **Execute Button**: Sends the request
- **Response Viewer**: Formatted JSON response

### Documentation
- **Endpoint Descriptions**: What each endpoint does
- **Parameter Descriptions**: Field explanations
- **Example Requests**: Pre-filled examples
- **Example Responses**: Sample responses for all status codes
- **Schema Definitions**: Detailed field information

### Schema Inspection
- Click on any model name to see:
  - Field types
  - Required vs optional
  - Constraints (min/max length, etc.)
  - Example values

## 🐛 Troubleshooting

### Swagger UI Not Loading

**Problem**: Page doesn't load or shows error

**Solutions**:
1. Check server is running: Look for "Uvicorn running" message
2. Check URL: Must be exactly `http://localhost:8000/docs`
3. Check port: Default is 8000, change if needed
4. Check firewall: Ensure port 8000 is not blocked

### "Try it out" Button Not Working

**Problem**: Can't edit request or execute

**Solutions**:
1. Make sure you clicked "Try it out" button
2. Refresh the page
3. Check browser console for errors (F12)
4. Try a different browser

### No Response or Timeout

**Problem**: Request executes but no response

**Solutions**:
1. Check server logs for errors
2. Verify vector database is populated (Step 1)
3. Check if handbook was processed successfully
4. Look for error messages in server console

### Empty Response or Low Confidence

**Problem**: Response says "don't have enough information"

**Solutions**:
1. Verify vector database has documents: Check logs for document count
2. Reprocess handbook: `python scripts/process_handbook.py --reset`
3. Try a different query related to the handbook content
4. Check if query is too vague or unrelated

### Authentication Errors

**Problem**: 401 Unauthorized error

**Solutions**:
1. Check if API key is required (check `.env` file)
2. Use "Authorize" button to set API key
3. Or remove `API_KEY` from `.env` to disable authentication

## 📊 Understanding Responses

### Response Fields

- **response**: The actual answer (main content)
- **language**: Detected/used language code
- **confidence**: 0.0 to 1.0 (higher is better)
  - > 0.8: High confidence
  - 0.5-0.8: Medium confidence
  - < 0.5: Low confidence
- **sources**: Document chunks used (for reference)
- **query_id**: Unique identifier for this query
- **conversation_id**: Use this for follow-up questions

### Confidence Scores

- **0.9-1.0**: Excellent match, very confident
- **0.7-0.9**: Good match, confident
- **0.5-0.7**: Moderate match, some confidence
- **< 0.5**: Low confidence, may need human review

## ✅ Verification Checklist

After following all steps, verify:

- [ ] Server starts without errors
- [ ] Swagger UI loads at http://localhost:8000/docs
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Query endpoint returns responses
- [ ] Responses contain relevant information
- [ ] Confidence scores are reasonable (> 0.5)
- [ ] Conversation memory works (follow-up questions)
- [ ] Language detection works (try different languages)

## 🎓 Next Steps

After successful local testing:

1. **Test More Scenarios**: Try different types of questions
2. **Test Multilingual**: Try queries in different languages
3. **Test Conversation Flow**: Test multi-turn conversations
4. **Integrate with n8n**: Use tested requests in n8n workflows
5. **Deploy to Azure**: When ready for production

## 📚 Additional Resources

- **Detailed Guide**: [SWAGGER_GUIDE.md](SWAGGER_GUIDE.md)
- **Local Testing**: [LOCAL_TESTING.md](LOCAL_TESTING.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Examples**: See Swagger UI examples section

## 💡 Pro Tips

1. **Bookmark Swagger UI**: Save http://localhost:8000/docs for quick access
2. **Use Examples**: Click "Example" buttons to auto-fill requests
3. **Copy Responses**: Use conversation_id from responses for follow-ups
4. **Check Logs**: Server console shows detailed request/response logs
5. **Test Edge Cases**: Try empty queries, very long queries, etc.

---

**Ready to test?** Start with Step 1 above! 🚀
