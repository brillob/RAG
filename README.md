# Multilingual RAG Student Support System

A production-ready Retrieval-Augmented Generation (RAG) system for handling high-volume student inquiries via WhatsApp, integrated with n8n workflow automation.

**Knowledge Base**: ICL Student Support Services Handbook (February 2022)
- Source: [ICL Student Support Services Handbook](https://www.icl.ac.nz/wp-content/uploads/2022/02/Student-Support-Services-Handbook-Feb-2022.pdf)

## Features

- **Real RAG with Local Vector Database**: Uses ChromaDB and sentence-transformers for local semantic search
- **Local LLM Support**: Run lightweight language models locally (Ollama or Transformers) - no API keys needed!
- **Actual Handbook Content**: Processes and indexes the real ICL Student Support Services Handbook
- **Multilingual Support**: Automatically detects and responds in the student's native language
- **Azure AI Search Integration**: Optional Azure deployment for production
- **Semantic Kernel**: Advanced AI orchestration with guardrails (Azure mode)
- **Hallucination Prevention**: Built-in guardrails to ensure accurate, knowledge-based responses
- **RESTful API**: Clean API interface for n8n integration
- **Containerized**: Ready for Azure Managed Endpoints deployment
- **Production Ready**: Error handling, logging, and monitoring capabilities

## Architecture

**Local Mode:**
```
n8n Workflow → API Endpoint → RAG Service → ChromaDB (Vector Search) → Local LLM (Ollama/Transformers) → Response
```

**Azure Mode:**
```
n8n Workflow → API Endpoint → RAG Service → Azure AI Search → Semantic Kernel → Response
```

## Quick Start

### Local Testing (Recommended First)

#### Option A: Using Anaconda/Conda (Recommended)

1. **Create and activate conda environment:**
   ```bash
   # Windows
   scripts\setup_conda.bat
   
   # Linux/Mac
   bash scripts/setup_conda.sh
   
   # Or manually:
   conda env create -f environment.yml
   conda activate rag-student-support
   ```

2. **Install dependencies (if not done automatically):**
   ```bash
   pip install -r requirements.txt
   ```

#### Option B: Using Python venv

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Process the handbook:**
   ```bash
   python scripts/process_handbook.py
   ```
   This downloads and indexes the ICL Student Support Services Handbook.

3. **Run the server:**
   ```bash
   python -m app.main
   ```

4. **Open Swagger UI:**
   - Open browser: **http://localhost:8000/docs**
   - Click **POST /api/v1/query**
   - Click **"Try it out"**
   - Test with example query

5. **Or test via command line:**
   ```bash
   python scripts/test_local.py --query "What are the enrolment requirements?"
   ```

See [RUN_SWAGGER_LOCALLY.md](RUN_SWAGGER_LOCALLY.md) for step-by-step Swagger UI guide.  
See [LOCAL_TESTING.md](LOCAL_TESTING.md) for detailed guide.

### Azure Deployment

1. **Deploy Azure resources:**
   ```bash
   python scripts/deploy_azure.py \
     --subscription <your-subscription-id> \
     --resource-group rag-student-support \
     --location eastus
   ```

2. **Configure environment:**
   ```bash
   cp .env.azure.example .env
   # Update .env with your Azure resource details
   ```

3. **Run the service:**
   ```bash
   python -m app.main
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

## Configuration

**Important:** The `.env` file is **OPTIONAL**. The application works with sensible defaults from `config.py`. You only need a `.env` file if you want to override defaults.

### How Configuration Works

1. **Defaults in `config.py`** - All settings have default values
2. **Optional `.env` file** - Override defaults by creating `.env` in the project root
3. **Environment variables** - Can also set environment variables directly

### Local Mode (Default - No Configuration Needed!)

The app works out of the box with defaults. To customize, create a `.env` file:

```env
# Optional: Override defaults
MODE=local
LOG_LEVEL=INFO
LOCAL_LLM_MODEL=tinyllama
LOCAL_LLM_PROVIDER=ollama
```

See `.env.example` for all available options.

### Azure Mode

```env
MODE=azure
AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_KEY=your-key
AZURE_SEARCH_INDEX_NAME=student-knowledge-base
AZURE_OPENAI_ENDPOINT=https://your-service.openai.azure.com
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

## API Documentation & Testing

### Swagger UI (Interactive Testing)

The API includes **interactive Swagger UI** for easy testing:

1. **Start the server:**
   ```bash
   python -m app.main
   ```

2. **Open Swagger UI:**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

3. **Test the API:**
   - Click on **POST /api/v1/query**
   - Click **"Try it out"**
   - Fill in the request body
   - Click **"Execute"**
   - View the response

**Quick Test Example:**
```json
{
  "query": "What are the enrolment requirements?",
  "language": "auto"
}
```

See [RUN_SWAGGER_LOCALLY.md](RUN_SWAGGER_LOCALLY.md) for complete step-by-step guide.

## API Endpoints

### POST /api/v1/query

Process a student inquiry and return a multilingual response.

**Request:**
```json
{
  "query": "What are the enrolment requirements?",
  "student_id": "optional_student_id",
  "language": "auto",
  "conversation_id": "optional_for_followups"
}
```

**Response:**
```json
{
  "response": "To enroll in ICL Graduate Business Programmes...",
  "language": "en",
  "confidence": 0.95,
  "sources": ["chunk_123", "chunk_124"],
  "query_id": "unique-query-id",
  "conversation_id": "use-this-for-followups"
}
```

### GET /health

Health check endpoint for monitoring.

### GET /

API information and available endpoints.

## Processing the Handbook

The system includes a script to automatically download and process the ICL handbook:

```bash
# Download and process automatically
python scripts/process_handbook.py

# Use local PDF file
python scripts/process_handbook.py --pdf path/to/handbook.pdf

# Reset database and reprocess
python scripts/process_handbook.py --reset
```

## Docker Deployment

### Local Testing

```bash
docker-compose up --build
```

### Azure Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Azure deployment instructions.

## Destroying Azure Resources

```bash
python scripts/destroy_azure.py \
  --resource-group rag-student-support \
  --yes
```

⚠️ **WARNING**: This permanently deletes all resources!

## Documentation

- **[RUN_SWAGGER_LOCALLY.md](RUN_SWAGGER_LOCALLY.md)** - Complete Swagger UI testing guide ⭐
- **[SWAGGER_QUICK_START.md](SWAGGER_QUICK_START.md)** - Quick Swagger UI reference
- **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Local testing with vector database
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Azure deployment guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture details

## Guardrails

The system includes multiple guardrails:
- Source verification: Only uses information from indexed documents
- Confidence scoring: Flags low-confidence responses
- Language validation: Ensures appropriate language detection
- Response length limits: Prevents overly verbose responses
- Content filtering: Blocks inappropriate content

## License

Proprietary - Internal Use Only
