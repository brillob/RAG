# Chunking Strategies Guide

This document explains the different chunking strategies available and when to use each.

## Available Strategies

### 1. Sentence-Based (Default)
**Strategy Name**: `sentence`

**How it works**:
- Splits text at sentence boundaries (`.`, `!`, `?`)
- Builds chunks by adding sentences until reaching `chunk_size`
- Applies overlap by taking the last N characters from previous chunk

**Pros**:
- Preserves complete thoughts
- Simple and fast
- Works well for most documents
- Maintains readability

**Cons**:
- May split related content across chunks
- Doesn't consider document structure
- Fixed overlap may not be optimal

**Best for**:
- General-purpose documents
- Well-structured text
- When you need fast processing

**Example**:
```bash
python scripts/process_handbook.py --strategy sentence
```

---

### 2. Section-Based
**Strategy Name**: `section`

**How it works**:
- First extracts document sections using headers
- Each section becomes a chunk (if small enough)
- Large sections are further split using sentence-based chunking
- Preserves section titles in metadata

**Pros**:
- Respects document structure
- Groups related content together
- Better for structured documents (handbooks, manuals)
- Section titles provide context

**Cons**:
- Requires identifiable section headers
- May create very large chunks if sections are big
- Less effective for unstructured text

**Best for**:
- Handbooks and manuals
- Documents with clear sections
- When structure matters

**Example**:
```bash
python scripts/process_handbook.py --strategy section
```

---

### 3. Semantic Chunking
**Strategy Name**: `semantic`

**How it works**:
- First creates sentence-based chunks
- Generates embeddings for each chunk
- Groups similar chunks together using cosine similarity
- Merges chunks with similarity > threshold (0.85)

**Pros**:
- Groups semantically related content
- Better context preservation
- Reduces chunk fragmentation
- More intelligent grouping

**Cons**:
- Requires embedding model (slower)
- More complex processing
- May create larger chunks
- Requires tuning similarity threshold

**Best for**:
- When semantic coherence is important
- Complex documents with related topics
- When you want fewer, more meaningful chunks

**Example**:
```bash
python scripts/process_handbook.py --strategy semantic
```

---

### 4. Recursive Character Splitting
**Strategy Name**: `recursive`

**How it works**:
- Hierarchical splitting using multiple separators
- Tries separators in order: paragraphs (`\n\n`), lines (`\n`), sentences (`. `), words (` `), characters
- Recursively splits until chunks fit size limit
- Applies overlap at the end

**Pros**:
- Very flexible
- Handles various text formats
- Guarantees chunk size limits
- Good for mixed content

**Cons**:
- May break sentences if needed
- More complex algorithm
- Can create many small chunks
- Less semantic awareness

**Best for**:
- Mixed format documents
- When strict size limits are needed
- Documents with varied structure

**Example**:
```bash
python scripts/process_handbook.py --strategy recursive
```

---

## Configuration

### Via Environment Variables

Add to `.env`:
```env
CHUNKING_STRATEGY=sentence  # or semantic, section, recursive
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### Via Command Line

```bash
python scripts/process_handbook.py \
  --strategy semantic \
  --chunk-size 800 \
  --chunk-overlap 100
```

## Comparison Table

| Strategy | Speed | Quality | Structure Aware | Best Use Case |
|----------|-------|---------|-----------------|---------------|
| Sentence | ⚡⚡⚡ | ⭐⭐⭐ | ❌ | General documents |
| Section | ⚡⚡ | ⭐⭐⭐⭐ | ✅ | Handbooks, manuals |
| Semantic | ⚡ | ⭐⭐⭐⭐⭐ | ⚠️ | Complex topics |
| Recursive | ⚡⚡ | ⭐⭐ | ❌ | Mixed formats |

## Recommendations for ICL Handbook

For the ICL Student Support Services Handbook, we recommend:

1. **Section-Based** (Primary choice)
   - Handbook has clear sections (Enrolment, Visas, Support, etc.)
   - Preserves logical grouping
   - Better retrieval for section-specific questions

2. **Semantic** (Alternative)
   - If you want more intelligent grouping
   - Better for complex multi-part questions
   - Requires more processing time

3. **Sentence-Based** (Fallback)
   - Fast and reliable
   - Good for general queries
   - Works if section detection fails

## Changing Strategy

To change the chunking strategy for an existing database:

```bash
# Reset and reprocess with new strategy
python scripts/process_handbook.py \
  --strategy section \
  --reset
```

**Note**: Changing strategy requires reprocessing the entire document.

## Performance Considerations

- **Sentence**: Fastest (~seconds)
- **Section**: Fast (~seconds to minutes)
- **Recursive**: Medium (~minutes)
- **Semantic**: Slowest (~minutes, requires embeddings)

## Tips

1. **Start with sentence-based** for quick testing
2. **Use section-based** for structured documents
3. **Try semantic** if retrieval quality is poor
4. **Adjust chunk_size** based on your embedding model's context window
5. **Increase overlap** if context is lost at boundaries
