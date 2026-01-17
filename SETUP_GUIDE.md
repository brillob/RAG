# Setup Guide - ICL Student Support RAG System

Complete setup guide for the RAG system using the ICL Student Support Services Handbook.

## Overview

This system uses:
- **ChromaDB**: Local vector database for semantic search
- **Sentence Transformers**: Local embeddings (no API calls)
- **ICL Student Handbook**: Real PDF from [ICL Education](https://www.icl.ac.nz/wp-content/uploads/2022/02/Student-Support-Services-Handbook-Feb-2022.pdf)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This will install:
- ChromaDB for vector storage
- sentence-transformers for embeddings (~80MB model download on first use)
- PDF processing libraries (pdfplumber, pypdf)

### 2. Download and Process the Handbook

The system can automatically download the handbook from ICL's website:

```bash
python scripts/process_handbook.py
```

This will:
1. Download the PDF from ICL's website
2. Extract all text content
3. Split into chunks (500 chars with 50 char overlap)
4. Generate embeddings using sentence-transformers
5. Store in ChromaDB vector database

**Output:**
- PDF saved to `./data/icl_handbook.pdf`
- Vector database created in `./chroma_db/`

### 3. Configure Environment

Create a `.env` file:

```bash
MODE=local
LOG_LEVEL=INFO
PORT=8000
VECTOR_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 4. Run the Server

```bash
python -m app.main
```

You should see:
```
INFO - Loaded existing collection 'student_handbook' with X documents
INFO - RAG Service initialized
INFO - Application startup complete.
```

### 5. Test the System

```bash
# Test health
curl http://localhost:8000/health

# Test a query
python scripts/test_local.py --query "What are the enrolment requirements?"
```

## How It Works

### Vector Database (ChromaDB)

- **Location**: `./chroma_db/` (configurable)
- **Collection**: `student_handbook`
- **Embeddings**: Generated automatically by ChromaDB using its default embedding function
- **Persistence**: Data persists between runs

### Embeddings

- **Model**: `all-MiniLM-L6-v2` (default, fast, English)
- **Alternative**: `paraphrase-multilingual-MiniLM-L12-v2` for multilingual support
- **Dimension**: 384 (for MiniLM models)
- **Storage**: Cached locally after first download

### PDF Processing

The handbook is processed into chunks:
- **Chunk Size**: 500 characters (default)
- **Overlap**: 50 characters (default)
- **Purpose**: Ensures context is preserved across chunk boundaries

## Customization

### Change Embedding Model

Edit `.env`:
```env
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

Then reprocess:
```bash
python scripts/process_handbook.py --reset
```

### Adjust Chunk Size

```bash
python scripts/process_handbook.py --chunk-size 1000 --chunk-overlap 100 --reset
```

### Use Local PDF

```bash
python scripts/process_handbook.py --pdf path/to/your/handbook.pdf
```

## Troubleshooting

### "No documents found" Error

The vector database is empty. Process the handbook:
```bash
python scripts/process_handbook.py
```

### Model Download Fails

The embedding model downloads on first use. If it fails:
1. Check internet connection
2. Manually download: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`
3. Model is cached in `~/.cache/torch/sentence_transformers/`

### PDF Processing Errors

If PDF extraction fails:
1. Ensure `pdfplumber` is installed: `pip install pdfplumber`
2. Try with `pypdf` as fallback (already included)
3. Check PDF is not corrupted
4. Download manually and use `--pdf` flag

### ChromaDB Errors

If ChromaDB has issues:
1. Delete `./chroma_db/` directory
2. Reprocess: `python scripts/process_handbook.py --reset`

## Verification

Check that everything is working:

```bash
# 1. Check vector database has documents
python -c "from app.services.vector_store import VectorStore; vs = VectorStore(); print(f'Documents: {vs.count()}')"

# 2. Test search
python -c "from app.services.vector_store import VectorStore; vs = VectorStore().search('enrolment requirements', n_results=3)"

# 3. Test full RAG
python scripts/test_local.py --query "How do I contact student support?"
```

## Next Steps

1. ✅ Process the handbook
2. ✅ Test locally
3. Deploy to Azure (optional) - see [DEPLOYMENT.md](DEPLOYMENT.md)
4. Integrate with n8n
5. Deploy to production

## Resources

- **ICL Handbook**: https://www.icl.ac.nz/wp-content/uploads/2022/02/Student-Support-Services-Handbook-Feb-2022.pdf
- **ChromaDB Docs**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/
