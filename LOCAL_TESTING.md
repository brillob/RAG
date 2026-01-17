# Local Testing Guide

This guide explains how to test the RAG system locally with the actual ICL Student Support Services Handbook using a local vector database.

## Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The first run will download the embedding model (~80MB), which may take a few minutes.

### Step 2: Process the Handbook PDF

Download and process the ICL Student Support Services Handbook:

```bash
python scripts/process_handbook.py
```

This will:
- Download the PDF from ICL's website
- Extract text content
- Chunk the text into manageable pieces
- Generate embeddings using a local model
- Store everything in ChromaDB (local vector database)

**Alternative:** If you already have the PDF:
```bash
python scripts/process_handbook.py --pdf path/to/handbook.pdf
```

### Step 3: Set Up Environment

```bash
# Copy local environment template
cp .env.local.example .env

# Or manually create .env with:
MODE=local
LOG_LEVEL=INFO
PORT=8000
```

### Step 4: Run the Server

```bash
python -m app.main
```

### Step 5: Open Swagger UI (Recommended)

**Open your browser and go to:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Test the API interactively:**
1. In Swagger UI, find **POST /api/v1/query**
2. Click **"Try it out"**
3. Paste this example:
   ```json
   {
     "query": "What are the enrolment requirements?"
   }
   ```
4. Click **"Execute"**
5. View the response!

**See [RUN_SWAGGER_LOCALLY.md](RUN_SWAGGER_LOCALLY.md) for detailed step-by-step guide.**

### Step 6: Test the API (Command Line)

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the admission requirements?",
    "language": "auto"
  }'
```

### Option 2: Run With Docker

1. **Build and run with docker-compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually:**
   ```bash
   # Build image
   docker build -t rag-student-support:local .
   
   # Run container
   docker run -p 8000:8000 \
     -e MODE=local \
     -e LOG_LEVEL=INFO \
     rag-student-support:local
   ```

## Local Mode Features

When `MODE=local`, the system uses:

- **ChromaDB Vector Database**: Local vector database storing the actual ICL Student Handbook
- **Sentence Transformers**: Local embeddings (no API calls needed)
- **Mock OpenAI Service**: Rule-based response generation (no API calls)
- **No Azure Dependencies**: Works completely offline
- **Real RAG**: Actual retrieval from the handbook using semantic search

### Knowledge Base

The system uses the actual **ICL Student Support Services Handbook** (February 2022) which includes:
- Student Support Team contacts
- Enrolment requirements and procedures
- Visa and insurance information
- Attendance policies
- Academic support services
- Student services (email, ID cards, library, etc.)
- Accommodation options
- Health and safety information
- Living in New Zealand guide
- Working in New Zealand
- Getting around (transport, driving)
- And much more!

The handbook is automatically downloaded and processed when you run `scripts/process_handbook.py`.

### Testing Different Queries

Try these sample queries based on the actual handbook:

```bash
# Enrolment questions
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What documents do I need for enrolment?"}'

# Visa questions
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What visa do I need to study at ICL?"}'

# Support questions
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I contact student support?"}'

# Accommodation questions
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What accommodation options are available?"}'

# Attendance questions
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the attendance policy?"}'
```

## Using the Test Script

Use the provided test script for easier testing:

```bash
python scripts/test_local.py --query "What are the admission requirements?"
```

With options:
```bash
python scripts/test_local.py \
  --url http://localhost:8000 \
  --query "What are the admission requirements?" \
  --language auto
```

## Switching to Azure Mode

When ready to test with Azure services:

1. **Update .env file:**
   ```bash
   MODE=azure
   AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
   AZURE_SEARCH_KEY=your-key
   AZURE_SEARCH_INDEX_NAME=your-index
   AZURE_OPENAI_ENDPOINT=https://your-service.openai.azure.com
   AZURE_OPENAI_API_KEY=your-key
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   ```

2. **Restart the server**

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env
PORT=8001

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill
```

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Vector Database Empty
If you get "no relevant documents found", you need to process the handbook first:
```bash
python scripts/process_handbook.py
```

### Embedding Model Download Issues
The first run downloads the model (~80MB). If it fails:
- Check your internet connection
- The model is cached, so subsequent runs are faster
- You can manually download: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`

### PDF Processing Errors
If PDF processing fails:
- Ensure `pdfplumber` or `pypdf` is installed: `pip install pdfplumber`
- Check that the PDF file is not corrupted
- Try downloading manually and using `--pdf` flag

## Next Steps

After local testing:
1. Deploy to Azure using `scripts/deploy_azure.py`
2. Configure your knowledge base in Azure AI Search
3. Switch to Azure mode and test with real services
4. Deploy to production
