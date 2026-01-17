# Confidence Score Guide

## Understanding Confidence Scores

The confidence score (0.0 to 1.0) indicates how confident the system is that the answer is accurate based on the retrieved documents.

### Score Ranges

| Score Range | Meaning | Quality |
|-------------|---------|---------|
| **0.8 - 1.0** | Very High Confidence | Excellent match, answer is highly reliable |
| **0.6 - 0.8** | High Confidence | Good match, answer is reliable |
| **0.4 - 0.6** | Medium Confidence | Moderate match, answer may need verification |
| **0.2 - 0.4** | Low Confidence | Weak match, answer may be incomplete |
| **0.0 - 0.2** | Very Low Confidence | Poor match, answer may be inaccurate |

## Why Low Confidence (0.02) Happens

### Problem: Incorrect Normalization

**Previous Issue:**
- ChromaDB returns scores in **0-1 range** (already normalized)
- Code was dividing by 10.0 (assuming 0-10 range like Azure Search)
- Result: Score of 0.2 became 0.02 (0.2 / 10.0)

**Example:**
```
ChromaDB distance: 0.8 (high distance = low similarity)
Converted to score: 1.0 - 0.8 = 0.2
Old normalization: 0.2 / 10.0 = 0.02 ❌ (too low!)
New normalization: Uses score directly with smart scaling ✅
```

### Fixed Calculation

The new confidence calculation:
1. **Uses scores directly** for local mode (ChromaDB scores are already 0-1)
2. **Applies smart scaling** to better distinguish good vs poor matches
3. **Boosts confidence** when multiple relevant results are found

## How to Improve Confidence Scores

### 1. Improve Query Quality

**Better queries = better matches = higher confidence**

```python
# ❌ Vague query
"What is it?"

# ✅ Specific query
"What are the enrolment requirements for international students?"
```

### 2. Improve Chunking Strategy

**Better chunks = better semantic matches**

Update in `.env`:
```env
CHUNKING_STRATEGY=semantic  # Better than sentence-based
CHUNK_SIZE=500
CHUNK_OVERLAP=100  # Increase overlap for better context
```

### 3. Use Better Embedding Model

**Better embeddings = better semantic understanding**

Update in `.env`:
```env
# For multilingual support
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# For English-only (better quality)
EMBEDDING_MODEL=all-mpnet-base-v2
```

### 4. Increase Number of Results

**More results = better coverage = higher confidence**

In `app/services/rag_service.py`, line 226:
```python
search_results = self.vector_store.search(
    query=query,
    n_results=10  # Increase from 5 to 10
)
```

### 5. Improve Document Quality

**Better documents = better matches**

- Ensure documents are well-structured
- Remove noise and irrelevant content
- Use clear headings and sections

## Testing Confidence Scores

### Check Current Scores

```python
from app.services.vector_store import VectorStore
from app.services.rag_service import RAGService
import asyncio

vs = VectorStore()
rag = RAGService()

# Test a query
result = asyncio.run(rag.process_query("What are the enrolment requirements?"))

print(f"Confidence: {result['confidence']}")
print(f"Sources: {len(result['sources'])}")
```

### Debug Search Scores

```python
from app.services.vector_store import VectorStore

vs = VectorStore()
results = vs.search("What are the enrolment requirements?", n_results=5)

for i, r in enumerate(results):
    print(f"Result {i+1}:")
    print(f"  Score: {r.get('score', 0.0):.3f}")
    print(f"  Content: {r.get('content', '')[:100]}...")
    print()
```

## Expected Confidence Ranges

### Good Queries (Should get 0.6+)

- "What are the enrolment requirements?"
- "How do I apply for admission?"
- "What are the tuition fees?"
- "What support services are available?"

### Medium Queries (Should get 0.4-0.6)

- "Tell me about the school"
- "What programs are offered?"
- "How to register?"

### Poor Queries (May get 0.2-0.4)

- "What is it?"
- "Tell me something"
- Very vague or unrelated questions

## Monitoring Confidence

### Set Minimum Confidence Threshold

In `app/config.py`:
```python
min_confidence_score: float = 0.5  # Reject answers below this
```

Or in `.env`:
```env
MIN_CONFIDENCE_SCORE=0.5
```

### Log Low Confidence Responses

The system already logs warnings for low confidence:
```python
if result["confidence"] < settings.min_confidence_score:
    logger.warning(f"Low confidence response: {result['confidence']}")
```

## Quick Fixes

### Fix 1: Re-process Documents with Better Settings

```bash
python scripts/process_handbook.py --strategy semantic --chunk-size 500 --chunk-overlap 100
```

### Fix 2: Use Better Embedding Model

```env
EMBEDDING_MODEL=all-mpnet-base-v2
```

Then re-process documents.

### Fix 3: Increase Search Results

Edit `app/services/rag_service.py`:
```python
n_results=10  # Instead of 5
```

## Summary

**0.02 confidence is BAD** - it means:
- ❌ Very poor match between query and documents
- ❌ Answer may be inaccurate or incomplete
- ❌ Documents may not contain relevant information

**After the fix:**
- ✅ Scores properly reflect similarity (0.0-1.0)
- ✅ Better distinction between good and poor matches
- ✅ More accurate confidence assessment

**To improve:**
1. Use specific, clear queries
2. Improve chunking strategy
3. Use better embedding model
4. Increase number of search results
5. Ensure documents are well-processed
