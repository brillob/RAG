# Debugging Guide for RAG System

This guide covers various debugging techniques for the RAG application.

## Important: Python Path Issue

**If you get `ModuleNotFoundError: No module named 'app'`:**

This happens when Python can't find the `app` module. **Solution:** Use the debug script or run as module:

```bash
# ✅ Use debug script (recommended)
python scripts/debug_rag_service.py

# ✅ Or run as module
python -m app.main
```

See `DEBUGGING_PYTHON_PATH.md` for detailed solutions.

## Quick Start: Enable Debug Logging

### Method 1: Environment Variable (Easiest)

```bash
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"
python -m app.main

# Windows CMD
set LOG_LEVEL=DEBUG
python -m app.main

# Linux/Mac
export LOG_LEVEL=DEBUG
python -m app.main
```

### Method 2: Create .env File

Create a `.env` file in the project root:

```env
LOG_LEVEL=DEBUG
```

Then run:
```bash
python -m app.main
```

### Method 3: Modify config.py Temporarily

In `app/config.py`, change:
```python
log_level: str = "DEBUG"  # Change from "INFO" to "DEBUG"
```

## Debugging Methods

### 1. Python Debugger (pdb)

Add breakpoints in your code:

```python
import pdb; pdb.set_trace()  # Python 3.7+
# or
breakpoint()  # Python 3.7+ (recommended)
```

**Example:**
```python
# In app/services/rag_service.py
async def process_query(self, query: str, ...):
    breakpoint()  # Execution stops here
    # Your code continues after typing 'c' (continue) in debugger
```

**Common pdb commands:**
- `n` (next line)
- `s` (step into function)
- `c` (continue)
- `l` (list code)
- `p variable_name` (print variable)
- `pp variable_name` (pretty print)
- `q` (quit)

### 2. IDE Debugging (VS Code / PyCharm)

#### VS Code

1. **Set breakpoints**: Click left of line number
2. **Start debugging**: Press `F5` or go to Run → Start Debugging
3. **Create launch.json**:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/app/main.py",
            "module": "app.main",
            "console": "integratedTerminal",
            "env": {
                "LOG_LEVEL": "DEBUG"
            },
            "justMyCode": false
        }
    ]
}
```

#### PyCharm

1. **Set breakpoints**: Click left of line number
2. **Create Run Configuration**:
   - Run → Edit Configurations
   - Add Python configuration
   - Script path: `app/main.py`
   - Environment variables: `LOG_LEVEL=DEBUG`
3. **Debug**: Click debug button or Shift+F9

### 3. Logging Levels

The application uses Python's logging module with these levels:

```python
# In order of verbosity (lowest to highest)
logging.CRITICAL  # Only critical errors
logging.ERROR     # Errors only
logging.WARNING   # Warnings and errors
logging.INFO      # Info, warnings, errors (default)
logging.DEBUG     # Everything (most verbose)
```

**Enable debug logging:**
```python
# In app/config.py or .env
LOG_LEVEL=DEBUG
```

### 4. View Logs in Real-Time

#### Terminal Output
When running the server, logs appear in the terminal:
```bash
python -m app.main
```

#### Log File (if configured)
Check if logging to file is enabled in `app/main.py`.

## Common Debugging Scenarios

### Scenario 1: Debug RAG Query Processing

**Problem:** Query not returning expected results

**Debug steps:**

1. **Enable debug logging:**
   ```bash
   LOG_LEVEL=DEBUG python -m app.main
   ```

2. **Add breakpoint in RAG service:**
   ```python
   # In app/services/rag_service.py
   async def process_query(self, query: str, ...):
       logger.debug(f"Processing query: {query}")
       breakpoint()  # Stop here to inspect
       
       search_results = await self._search_knowledge_base(...)
       logger.debug(f"Search results: {search_results}")
   ```

3. **Check vector store:**
   ```python
   from app.services.vector_store import VectorStore
   vs = VectorStore()
   print(f"Documents in store: {vs.count()}")
   ```

### Scenario 2: Debug Local LLM Issues

**Problem:** Local LLM not responding

**Debug steps:**

1. **Check Ollama is running:**
   ```bash
   ollama list
   ```

2. **Test Ollama directly:**
   ```bash
   ollama run tinyllama "Hello"
   ```

3. **Add debug logging:**
   ```python
   # In app/services/local_llm.py
   async def _generate_ollama(self, ...):
       logger.debug(f"Calling Ollama with model: {self.model_name}")
       logger.debug(f"Prompt: {prompt[:100]}...")
       breakpoint()  # Inspect before API call
   ```

4. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   # Or visit: http://localhost:8000/health
   ```

### Scenario 3: Debug Vector Search

**Problem:** Search not finding relevant documents

**Debug steps:**

1. **Test vector store directly:**
   ```python
   from app.services.vector_store import VectorStore
   from app.services.embeddings import EmbeddingService
   
   vs = VectorStore()
   emb = EmbeddingService()
   
   query = "What are the enrolment requirements?"
   query_embedding = emb.generate_embedding(query)
   
   results = vs.search(query_embedding, top_k=5)
   print(f"Found {len(results)} results")
   for r in results:
       print(f"Score: {r.get('score')}, Content: {r.get('content')[:100]}")
   ```

2. **Check embeddings:**
   ```python
   embedding = emb.generate_embedding("test query")
   print(f"Embedding shape: {embedding.shape}")
   print(f"Embedding sample: {embedding[:5]}")
   ```

### Scenario 4: Debug API Endpoints

**Problem:** API endpoint not working

**Debug steps:**

1. **Use Swagger UI:**
   - Visit: http://localhost:8000/docs
   - Test endpoints interactively
   - See request/response details

2. **Use curl:**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Query endpoint
   curl -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the enrolment requirements?"}'
   ```

3. **Add request logging:**
   ```python
   # In app/main.py
   @app.post("/api/v1/query")
   async def process_query(request: QueryRequest, ...):
       logger.debug(f"Received request: {request.dict()}")
       breakpoint()  # Inspect request
   ```

### Scenario 5: Debug Configuration

**Problem:** Settings not loading correctly

**Debug steps:**

1. **Print current settings:**
   ```python
   from app.config import settings
   
   print(f"Mode: {settings.mode}")
   print(f"LLM Model: {settings.local_llm_model}")
   print(f"LLM Provider: {settings.local_llm_provider}")
   print(f"Log Level: {settings.log_level}")
   ```

2. **Check environment variables:**
   ```bash
   # Windows PowerShell
   Get-ChildItem Env: | Where-Object Name -like "*LLM*"
   
   # Linux/Mac
   env | grep LLM
   ```

3. **Verify .env file:**
   ```bash
   # Check if .env exists
   ls .env  # Linux/Mac
   dir .env  # Windows
   ```

## Debugging Tools

### 1. Python Debugger (pdb)

```python
import pdb
pdb.set_trace()  # or breakpoint()
```

### 2. IPython Debugger (ipdb) - Better than pdb

**Install:**
```bash
pip install ipdb
```

**Use:**
```python
import ipdb; ipdb.set_trace()
```

**Advantages:**
- Better syntax highlighting
- Tab completion
- Better error messages

### 3. Logging with Context

Add context to logs:

```python
import logging

logger = logging.getLogger(__name__)

# Add context
logger.debug("Processing query", extra={
    "query": query,
    "student_id": student_id,
    "conversation_id": conversation_id
})
```

### 4. Print Debugging (Quick & Dirty)

```python
print(f"[DEBUG] Query: {query}")
print(f"[DEBUG] Search results: {search_results}")
print(f"[DEBUG] Response: {response}")
```

### 5. Assertions

```python
assert len(search_results) > 0, "No search results found!"
assert response is not None, "Response is None!"
```

## Debugging Checklist

When debugging, check:

- [ ] **Logs**: Are logs showing? Check `LOG_LEVEL=DEBUG`
- [ ] **Environment**: Is conda environment activated?
- [ ] **Dependencies**: Are all packages installed?
- [ ] **Services**: Is Ollama running? (if using local LLM)
- [ ] **Data**: Is vector store populated? (`vs.count()`)
- [ ] **Configuration**: Are settings correct? (print `settings`)
- [ ] **Network**: Is server running? (check `http://localhost:8000/health`)
- [ ] **API**: Test with Swagger UI or curl

## Quick Debug Commands

```bash
# Check vector store
python -c "from app.services.vector_store import VectorStore; vs = VectorStore(); print(f'Documents: {vs.count()}')"

# Check configuration
python -c "from app.config import settings; print(f'Mode: {settings.mode}, LLM: {settings.local_llm_model}')"

# Test Ollama
ollama list
ollama run tinyllama "test"

# Check health
curl http://localhost:8000/health

# Run with debug logging
LOG_LEVEL=DEBUG python -m app.main
```

## Advanced Debugging

### 1. Profiling Performance

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
await rag_service.process_query("test query")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

### 2. Memory Debugging

```bash
pip install memory-profiler

# Add decorator
@profile
def your_function():
    # code
    pass

# Run with
python -m memory_profiler your_script.py
```

### 3. Async Debugging

For async code, use:
```python
import asyncio
import logging

# Enable asyncio debug mode
asyncio.get_event_loop().set_debug(True)
logging.basicConfig(level=logging.DEBUG)
```

## Getting Help

If you're stuck:

1. **Check logs**: Look for ERROR or WARNING messages
2. **Check Swagger UI**: Test endpoints interactively
3. **Check health endpoint**: Verify services are running
4. **Print variables**: Add `print()` or `logger.debug()` statements
5. **Use breakpoints**: Step through code with debugger

## Example: Complete Debug Session

```python
# 1. Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. Import and check config
from app.config import settings
print(f"Config: {settings.local_llm_model}")

# 3. Test vector store
from app.services.vector_store import VectorStore
vs = VectorStore()
print(f"Documents: {vs.count()}")

# 4. Test RAG service
from app.services.rag_service import RAGService
import asyncio

rag = RAGService()
result = asyncio.run(rag.process_query("test query"))
print(f"Result: {result}")

# 5. Add breakpoint for detailed inspection
breakpoint()  # Inspect variables here
```
