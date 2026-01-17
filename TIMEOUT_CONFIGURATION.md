# Timeout Configuration Guide

## Debug Mode Timeout (120 seconds)

**For debug mode, timeouts are automatically set to 120 seconds** when `LOG_LEVEL=DEBUG`.

**Scripts with debug timeout:**
- `scripts/test_api_simple.py` - Uses 120s when `LOG_LEVEL=DEBUG`
- `scripts/test_local.py` - Uses 120s when `LOG_LEVEL=DEBUG`
- `scripts/debug_api.py` - Always uses 120s (debug script)

**To enable debug timeout:**
```bash
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"
python scripts/test_api_simple.py

# Or use the dedicated debug script
python scripts/debug_api.py
```

## Where Timeouts Are Set

### 1. Ollama Client Timeout (Local LLM)

**Location:** `app/services/local_llm.py` line 64

**Current:** 120 seconds (2 minutes)

**Configuration:** Set in `app/config.py`:
```python
ollama_timeout: float = 120.0  # Ollama client timeout in seconds
```

**How to change:**
- In `.env` file: `OLLAMA_TIMEOUT=300` (5 minutes)
- Or modify `app/config.py` directly

### 2. API Request Timeout (FastAPI/Uvicorn)

**Location:** `app/config.py`

**Current:** 300 seconds (5 minutes) - newly added

**Configuration:**
```python
api_timeout: int = 300  # API request timeout in seconds
```

**How to change:**
- In `.env` file: `API_TIMEOUT=600` (10 minutes)
- Or modify `app/config.py` directly

### 3. Client Script Timeouts

**Location:** Various test scripts

**Current:** 30 seconds (default for `requests` library)

**Files:**
- `scripts/test_api_simple.py` - line 49: `timeout=30`
- `scripts/test_local.py` - line 30: `timeout=30`
- `scripts/process_handbook.py` - line 50: `timeout=30`

**How to change:** Modify the `timeout` parameter in these scripts

## Common Timeout Errors

### Error: "Read timed out. (read timeout=30)"

**Cause:** Client script timeout (30 seconds default)

**Solution 1: Increase client timeout**
```python
# In your script
response = requests.post(url, json=payload, timeout=300)  # 5 minutes
```

**Solution 2: Increase server timeout**
```env
# In .env file
API_TIMEOUT=600
OLLAMA_TIMEOUT=300
```

### Error: Ollama Connection Timeout

**Cause:** Ollama is taking too long to respond

**Solution:**
```env
# In .env file
OLLAMA_TIMEOUT=300  # Increase to 5 minutes
```

### Error: FastAPI Request Timeout

**Cause:** The entire request (including LLM inference) takes too long

**Solution:**
```env
# In .env file
API_TIMEOUT=600  # Increase to 10 minutes
```

## Recommended Timeout Values

| Scenario | Recommended Timeout | Reason |
|----------|-------------------|--------|
| **Local LLM (Ollama)** | 120-300 seconds | Model inference can be slow |
| **Transformers** | 180-600 seconds | First run loads model, slower |
| **API Requests** | 300-600 seconds | Includes search + LLM generation |
| **Health Checks** | 5-10 seconds | Should be fast |
| **PDF Download** | 30-60 seconds | Network dependent |

## Quick Fixes

### Fix 1: Increase All Timeouts

Create `.env` file:
```env
API_TIMEOUT=600
OLLAMA_TIMEOUT=300
```

### Fix 2: Increase Client Script Timeout

Edit `scripts/test_api_simple.py`:
```python
response = requests.post(url, json=payload, timeout=300)  # Changed from 30
```

### Fix 3: Increase Uvicorn Timeout

Edit `app/main.py`:
```python
uvicorn.run(
    "app.main:app",
    host=settings.host,
    port=settings.port,
    log_level=settings.log_level.lower(),
    timeout_keep_alive=300  # Add this
)
```

## Debugging Timeout Issues

### Check Current Timeouts

```python
from app.config import settings
print(f"API Timeout: {settings.api_timeout}s")
print(f"Ollama Timeout: {settings.ollama_timeout}s")
```

### Test with Longer Timeout

```python
import requests
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={"query": "test"},
    timeout=600  # 10 minutes
)
```

### Check Server Logs

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

Then check logs for slow operations.

## Why Timeouts Happen

1. **LLM Inference is Slow**
   - First request: Model loading (can take 30-60 seconds)
   - Subsequent requests: Still 10-30 seconds per query
   - Solution: Increase `OLLAMA_TIMEOUT`

2. **Large Context**
   - More context = longer processing
   - Solution: Reduce `chunk_size` or `max_response_length`

3. **CPU-Only Inference**
   - Much slower than GPU
   - Solution: Use smaller model or enable GPU

4. **Network Issues**
   - Slow connection to Ollama
   - Solution: Check Ollama is running locally

## Configuration Examples

### For Fast Development (Smaller Timeouts)

```env
API_TIMEOUT=120
OLLAMA_TIMEOUT=60
```

### For Production (Larger Timeouts)

```env
API_TIMEOUT=600
OLLAMA_TIMEOUT=300
```

### For Slow Hardware

```env
API_TIMEOUT=900
OLLAMA_TIMEOUT=600
```

## Testing Timeout Settings

```bash
# Test with custom timeout
python -c "
import requests
try:
    response = requests.post(
        'http://localhost:8000/api/v1/query',
        json={'query': 'test'},
        timeout=600
    )
    print('Success!')
except requests.exceptions.Timeout:
    print('Timeout! Increase timeout or check server.')
"
```
