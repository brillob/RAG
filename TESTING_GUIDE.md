# Testing Guide - How to Test While Server is Running

When the FastAPI server is running, you can't use that terminal for commands. Here are several ways to test your API:

## 🚀 Quick Start

### Option 1: Open Swagger UI (Easiest!)

1. **Keep the server running** in the current terminal
2. **Open your web browser**
3. **Navigate to:** http://localhost:8000/docs
4. **Click on** `POST /api/v1/query`
5. **Click "Try it out"**
6. **Enter a query** like: `"What are the enrolment requirements?"`
7. **Click "Execute"**

This is the easiest way - no need for separate terminals!

### Option 2: Use a New Terminal Window

1. **Keep the server running** in Terminal 1
2. **Open a NEW terminal window/tab** (Terminal 2)
3. **Activate conda environment:**
   ```bash
   conda activate rag-student-support
   cd C:\Users\brill\CursorProject\RAG
   ```
4. **Run the test script:**
   ```bash
   python scripts/test_api_simple.py
   ```
   
   Or with a custom query:
   ```bash
   python scripts/test_api_simple.py "What are the admission requirements?"
   ```

### Option 3: Use curl (New Terminal)

In a new terminal:
```bash
# Test health
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What are the enrolment requirements?\"}"
```

## 📋 Available Test Scripts

### 1. `scripts/test_api_simple.py` (Recommended)
Simple, user-friendly test script:
```bash
python scripts/test_api_simple.py
python scripts/test_api_simple.py "Your question here"
```

### 2. `scripts/test_local.py`
Original test script with more options:
```bash
python scripts/test_local.py --query "What are the enrolment requirements?"
python scripts/test_local.py --query "How do I apply?" --language "en"
```

## 🌐 Swagger UI Endpoints

Once you open http://localhost:8000/docs, you can test:

### Health Check
- **GET** `/health` - Check if server is running

### Query Endpoint
- **POST** `/api/v1/query` - Ask questions
  - Request body:
    ```json
    {
      "query": "What are the enrolment requirements?",
      "language": "auto",
      "student_id": "optional_student_id",
      "conversation_id": "optional_conversation_id"
    }
    ```

### API Documentation
- **GET** `/docs` - Swagger UI (interactive)
- **GET** `/redoc` - ReDoc (alternative docs)
- **GET** `/openapi.json` - OpenAPI schema

## 🔍 Testing Different Scenarios

### Test 1: Basic Query
```bash
python scripts/test_api_simple.py "What are the enrolment requirements?"
```

### Test 2: Follow-up Question (with conversation_id)
1. First query:
   ```bash
   python scripts/test_api_simple.py "What are the enrolment requirements?"
   ```
   Note the `conversation_id` from the response

2. Follow-up (in Swagger UI or with curl):
   ```json
   {
     "query": "What documents do I need?",
     "conversation_id": "paste_conversation_id_here"
   }
   ```

### Test 3: Different Languages
```bash
python scripts/test_local.py --query "¿Cuáles son los requisitos de inscripción?" --language "es"
```

### Test 4: Health Check
```bash
curl http://localhost:8000/health
```

## 🛠 Troubleshooting

### Issue: "Cannot connect to server"
**Solution:** Make sure the server is running in another terminal:
```bash
python -m app.main
```

### Issue: "Connection refused"
**Solution:** 
- Check if server is running on port 8000
- Try: http://localhost:8000/health in browser
- Check firewall settings

### Issue: "401 Unauthorized"
**Solution:** If API key is required, check your `.env` file and include it in requests:
```bash
python scripts/test_local.py --query "test" --api-key "your-api-key"
```

### Issue: "Module not found" in test script
**Solution:** Make sure you're in the conda environment:
```bash
conda activate rag-student-support
```

## 💡 Pro Tips

1. **Use Swagger UI** - It's the easiest way to test and explore the API
2. **Keep server running** - Don't close the terminal where the server is running
3. **Use new terminal** - Open a separate terminal for running test scripts
4. **Check logs** - The server terminal shows all requests and responses
5. **Test conversation memory** - Use the same `conversation_id` for follow-up questions

## 📝 Example Test Session

```bash
# Terminal 1: Start server
conda activate rag-student-support
python -m app.main

# Terminal 2: Run tests
conda activate rag-student-support
cd C:\Users\brill\CursorProject\RAG

# Test health
python scripts/test_api_simple.py

# Test query
python scripts/test_api_simple.py "What are the admission requirements?"

# Or use Swagger UI in browser
# Open: http://localhost:8000/docs
```

## 🎯 Quick Reference

| Method | Command | Best For |
|--------|---------|----------|
| Swagger UI | http://localhost:8000/docs | Interactive testing |
| Test Script | `python scripts/test_api_simple.py` | Automated testing |
| curl | `curl http://localhost:8000/health` | Quick checks |
| Browser | http://localhost:8000/health | Visual verification |
