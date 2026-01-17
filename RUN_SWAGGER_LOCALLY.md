# Run Swagger UI Locally - Complete Guide

Complete step-by-step instructions to run and test the API using Swagger UI on your local machine.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Internet connection (for downloading handbook PDF)
- [ ] Web browser (Chrome, Firefox, Edge, etc.)

## 🚀 Complete Setup & Testing Steps

### Step 1: Verify Python Installation

```bash
python --version
# Should show Python 3.10 or higher
```

If Python is not installed:
- **Windows**: Download from python.org or Microsoft Store
- **Mac**: `brew install python3`
- **Linux**: `sudo apt-get install python3`

### Step 2: Install Dependencies

```bash
# Navigate to project directory
cd c:\Users\brill\CursorProject\RAG

# Install all required packages
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

**Troubleshooting:**
- If `pip` not found: Use `python -m pip` instead
- If permission errors: Use `pip install --user -r requirements.txt`
- If package conflicts: Create virtual environment first

### Step 3: Process the ICL Handbook

This step downloads and indexes the student handbook:

```bash
python scripts/process_handbook.py
```

**What Happens:**
1. Downloads PDF from ICL website
2. Extracts text content
3. Chunks text using selected strategy
4. Generates embeddings
5. Stores in ChromaDB vector database

**Expected Output:**
```
🚀 Processing ICL Student Support Services Handbook...
INFO: Downloading PDF from https://www.icl.ac.nz/...
✓ Downloaded PDF to ./data/icl_handbook.pdf
INFO: Extracting text from PDF...
✓ Extracted 50000+ characters from PDF
INFO: Chunking text using sentence strategy...
✓ Created 150+ chunks
INFO: Generating embeddings and adding to vector database...
✓ Added 150+ documents to vector database
✓ Processing complete!
```

**Troubleshooting:**
- **Download fails**: Check internet connection, try again
- **PDF extraction fails**: Install `pdfplumber`: `pip install pdfplumber`
- **Processing slow**: Normal for first run (embedding model download)

### Step 4: Configure Environment (Optional)

Create `.env` file if you want custom settings:

```bash
# Create .env file
MODE=local
LOG_LEVEL=INFO
PORT=8000
ENABLE_CONVERSation_MEMORY=true
```

**Note**: If `.env` doesn't exist, defaults will be used.

### Step 5: Start the FastAPI Server

```bash
python -m app.main
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Loaded existing collection 'student_handbook' with 150 documents
INFO:     RAG Service initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal window open!** The server must be running.

**Troubleshooting:**
- **Port 8000 in use**: 
  - Change port: Edit `.env` and set `PORT=8001`
  - Or kill process: `netstat -ano | findstr :8000` then `taskkill /PID <PID> /F`
- **Import errors**: Run `pip install -r requirements.txt` again
- **Vector DB empty**: Run Step 3 first

### Step 6: Open Swagger UI in Browser

1. **Open your web browser** (Chrome, Firefox, Edge, Safari)
2. **Navigate to**: http://localhost:8000/docs
3. **You should see**: Swagger UI interface with API documentation

**Alternative URLs:**
- **ReDoc** (alternative docs): http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

**Troubleshooting:**
- **Page not loading**: 
  - Check server is running (Step 5)
  - Check URL is exactly `http://localhost:8000/docs`
  - Try `http://127.0.0.1:8000/docs`
- **Connection refused**: Server not running, go back to Step 5

### Step 7: Test Health Endpoint

1. In Swagger UI, find **GET /health** (under "Monitoring" section)
2. Click on it to expand
3. Click the **"Try it out"** button (top right of endpoint)
4. Click the **"Execute"** button (blue button at bottom)
5. Scroll down to see **"Response"** section

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

✅ **If you see this, the server is working correctly!**

### Step 8: Test Query Endpoint (Main Feature)

1. In Swagger UI, find **POST /api/v1/query** (under "Student Queries" section)
2. Click on it to expand
3. Click **"Try it out"** button
4. You'll see a request body editor with an example
5. **Replace the example** with:
   ```json
   {
     "query": "What are the enrolment requirements?"
   }
   ```
6. Click **"Execute"** button
7. Scroll down to **"Response body"** section

**Expected Response:**
```json
{
  "response": "To enroll in ICL Graduate Business Programmes, both domestic and international students are required to have a valid visa, suitable travel/medical insurance, and enough funds...",
  "language": "en",
  "confidence": 0.95,
  "sources": ["chunk_1", "chunk_2"],
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": "abc-123-def-456"
}
```

✅ **If you see a response with enrolment information, the RAG system is working!**

### Step 9: Test Follow-up Question (Conversation Memory)

1. **Copy the `conversation_id`** from the previous response
2. In Swagger UI, create a new request:
   ```json
   {
     "query": "Do I need insurance?",
     "conversation_id": "paste-conversation-id-here"
   }
   ```
3. Click **"Execute"**
4. The response should understand the context from the first question

**Expected**: Response mentions insurance in the context of enrolment requirements.

✅ **If the response understands context, conversation memory is working!**

### Step 10: Test More Scenarios

Try these additional test cases in Swagger UI:

#### Test Case 1: Visa Question
```json
{
  "query": "What visa do I need to study at ICL?",
  "language": "en"
}
```

#### Test Case 2: Multilingual Query
```json
{
  "query": "¿Cuáles son los requisitos de admisión?",
  "language": "auto"
}
```

#### Test Case 3: Student Support Contact
```json
{
  "query": "How do I contact student support?",
  "student_id": "student123"
}
```

#### Test Case 4: Query with No Results
```json
{
  "query": "What is the weather today?"
}
```
Expected: Low confidence response indicating insufficient information.

## 🎯 Swagger UI Features Guide

### Navigation

- **Collapse/Expand**: Click endpoint names to expand/collapse
- **Search**: Use browser search (Ctrl+F) to find endpoints
- **Tags**: Endpoints are organized by tags (Student Queries, Monitoring, Information)

### Interactive Testing

1. **"Try it out" Button**: 
   - Makes the endpoint editable
   - Appears at top right of each endpoint
   - Click to enable testing mode

2. **Request Body Editor**:
   - JSON editor with syntax highlighting
   - Pre-filled with examples
   - Edit directly in browser

3. **Execute Button**:
   - Sends the HTTP request
   - Shows loading indicator
   - Displays response below

4. **Response Viewer**:
   - Formatted JSON
   - Color-coded
   - Expandable/collapsible
   - Copy button available

### Authentication

If API key is required:

1. Click **"Authorize"** button (top right, lock icon)
2. Enter your API key
3. Click **"Authorize"**
4. Click **"Close"**
5. All requests will include the API key automatically

**Note**: If `API_KEY` is not set in `.env`, authentication is disabled.

### Schema Inspection

Click on any model name (e.g., `QueryRequest`, `QueryResponse`) to see:
- Field descriptions
- Data types
- Required vs optional fields
- Constraints (min/max length, etc.)
- Example values

## 📊 Understanding Test Results

### Response Fields

- **response**: The actual answer (main content)
- **language**: Language code used (e.g., "en", "es")
- **confidence**: 0.0 to 1.0
  - **0.9-1.0**: Excellent match
  - **0.7-0.9**: Good match
  - **0.5-0.7**: Moderate match
  - **< 0.5**: Low confidence
- **sources**: Document chunk IDs used
- **query_id**: Unique identifier for this query
- **conversation_id**: Use for follow-up questions

### Status Codes

- **200 OK**: Successful request
- **401 Unauthorized**: Invalid/missing API key
- **422 Validation Error**: Invalid request format
- **500 Internal Server Error**: Server-side error

## 🐛 Common Issues & Solutions

### Issue 1: "Vector database is empty"

**Symptoms**: Response says "don't have enough information"

**Solution**:
```bash
python scripts/process_handbook.py --reset
```

### Issue 2: Server won't start

**Symptoms**: Error when running `python -m app.main`

**Solutions**:
1. Check Python version: `python --version` (need 3.10+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check for port conflicts: Change `PORT=8001` in `.env`

### Issue 3: Swagger UI shows errors

**Symptoms**: Red error messages in Swagger UI

**Solutions**:
1. Check server is running
2. Refresh browser page
3. Clear browser cache
4. Try different browser

### Issue 4: No response or timeout

**Symptoms**: Request executes but hangs or times out

**Solutions**:
1. Check server logs for errors
2. Verify vector database has documents
3. Check if embedding model is downloaded
4. Try simpler query

### Issue 5: Low confidence scores

**Symptoms**: Confidence < 0.5

**Solutions**:
1. Try more specific queries
2. Use keywords from the handbook
3. Check if handbook was processed correctly
4. Reprocess handbook: `python scripts/process_handbook.py --reset`

## ✅ Verification Checklist

After completing all steps, verify:

- [ ] Server starts without errors
- [ ] Swagger UI loads at http://localhost:8000/docs
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Query endpoint returns responses
- [ ] Responses contain relevant information
- [ ] Confidence scores are reasonable (> 0.5)
- [ ] Conversation memory works (follow-up questions)
- [ ] Language detection works
- [ ] Different query types work

## 🎓 Next Steps After Testing

Once Swagger UI testing is successful:

1. **Test More Scenarios**: Try different question types
2. **Test Multilingual**: Test queries in different languages
3. **Test Conversation Flow**: Test multi-turn conversations
4. **Review Responses**: Check response quality and accuracy
5. **Integrate with n8n**: Use tested requests in n8n workflows
6. **Deploy to Production**: When ready, deploy to Azure

## 📚 Additional Resources

- **Detailed Swagger Guide**: [SWAGGER_GUIDE.md](SWAGGER_GUIDE.md)
- **Quick Start**: [QUICK_START_SWAGGER.md](QUICK_START_SWAGGER.md)
- **Local Testing**: [LOCAL_TESTING.md](LOCAL_TESTING.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## 💡 Pro Tips

1. **Keep Server Running**: Don't close the terminal where server is running
2. **Bookmark Swagger UI**: Save http://localhost:8000/docs for quick access
3. **Use Examples**: Click "Example" buttons to auto-fill requests
4. **Copy Conversation IDs**: Save conversation_id for follow-up testing
5. **Check Server Logs**: Terminal shows detailed request/response information
6. **Test Edge Cases**: Try empty queries, very long queries, special characters

---

**Ready?** Start with Step 1 and work through each step! 🚀
