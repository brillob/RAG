# Application Architecture & File Structure

Complete explanation of the RAG Student Support System architecture, file structure, and data flow.

## 📁 Project Structure

```
RAG/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── models.py                # Pydantic data models
│   ├── utils.py                 # Utility functions
│   └── services/                # Core business logic services
│       ├── __init__.py
│       ├── rag_service.py       # Main RAG orchestration
│       ├── vector_store.py      # ChromaDB vector database
│       ├── embeddings.py        # Sentence transformers
│       ├── pdf_processor.py     # PDF extraction & chunking
│       ├── language_detector.py # Multilingual support
│       ├── conversation_memory.py # Conversation history
│       ├── azure_search.py      # Azure AI Search (production)
│       ├── mock_search.py       # Mock search (deprecated)
│       └── mock_openai.py       # Mock OpenAI (local mode)
│
├── scripts/                      # Utility scripts
│   ├── process_handbook.py      # PDF processing script
│   ├── test_local.py            # API testing script
│   ├── deploy_azure.py          # Azure deployment
│   ├── destroy_azure.py         # Azure cleanup
│   └── setup_local.*            # Local setup scripts
│
├── deployment/                   # Deployment configs
│   ├── azure-managed-endpoint.yaml
│   └── n8n-workflow-example.json
│
├── tests/                        # Unit tests
├── requirements.txt              # Dependencies
└── Dockerfile                    # Container definition
```

---

## 📄 File-by-File Explanation

### 🎯 Core Application Files

#### `app/main.py` - **Application Entry Point**
**Purpose**: FastAPI web server that handles HTTP requests

**Responsibilities**:
- Initializes FastAPI application with Swagger UI
- Sets up CORS middleware for n8n integration
- Defines API endpoints (`/health`, `/api/v1/query`)
- Handles authentication (API key verification)
- Routes requests to RAG service
- Returns formatted responses
- Provides interactive API documentation (Swagger UI)

**Key Components**:
- `app`: FastAPI instance with OpenAPI/Swagger documentation
- `rag_service`: Singleton RAG service instance
- `verify_api_key()`: Authentication middleware
- `process_query()`: Main query endpoint handler
- Swagger UI: Interactive API testing at `/docs`
- ReDoc: Alternative documentation at `/redoc`

**API Documentation**:
- **Swagger UI**: http://localhost:8000/docs (interactive testing)
- **ReDoc**: http://localhost:8000/redoc (alternative docs)
- **OpenAPI JSON**: http://localhost:8000/openapi.json

**Connections**:
- → `app.config.settings` (configuration)
- → `app.models` (request/response models)
- → `app.services.rag_service` (core logic)
- → `app.openapi_tags` (Swagger UI tags)

---

#### `app/config.py` - **Configuration Management**
**Purpose**: Centralized configuration using Pydantic Settings

**Responsibilities**:
- Loads environment variables from `.env` file
- Provides type-safe configuration access
- Defines default values
- Mode detection (local vs Azure)

**Key Settings**:
- `mode`: "local" or "azure"
- `chunking_strategy`: Chunking method
- `enable_conversation_memory`: Memory toggle
- Azure service credentials (when in Azure mode)
- Local vector DB settings

**Connections**:
- ← Used by: All service files
- → Environment variables (`.env` file)

---

#### `app/models.py` - **Data Models**
**Purpose**: Pydantic models for API request/response validation

**Models**:
- `QueryRequest`: Incoming student query with optional conversation_id
- `QueryResponse`: Response with answer, confidence, sources, conversation_id
- `HealthResponse`: Health check response

**Connections**:
- ← Used by: `app.main` (API endpoints)
- → FastAPI automatic validation

---

### 🔧 Service Layer Files

#### `app/services/rag_service.py` - **RAG Orchestrator** ⭐
**Purpose**: Main service that orchestrates the entire RAG pipeline

**Responsibilities**:
- Coordinates all RAG components
- Handles conversation memory
- Manages local vs Azure mode
- Orchestrates: search → context building → response generation
- Applies guardrails to prevent hallucination

**Key Methods**:
- `process_query()`: Main entry point for processing queries
- `_generate_response_local()`: Local mode response generation
- `_generate_response()`: Azure mode response generation
- `_build_context()`: Combines search results into context
- `_calculate_confidence()`: Computes response confidence
- `_apply_guardrails()`: Validates and filters responses

**Connections**:
- → `vector_store` (local mode) or `azure_search` (Azure mode)
- → `conversation_memory` (conversation history)
- → `language_detector` (language detection)
- → `mock_openai` (local) or Semantic Kernel (Azure)
- ← Called by: `app.main`

**Flow**:
```
Query → Language Detection → Memory Retrieval → Vector Search → 
Context Building → Response Generation → Guardrails → Memory Storage → Response
```

---

#### `app/services/vector_store.py` - **Vector Database**
**Purpose**: ChromaDB wrapper for local vector storage

**Responsibilities**:
- Manages ChromaDB collection
- Stores document embeddings
- Performs semantic search
- Handles persistence

**Key Methods**:
- `add_documents()`: Index documents with embeddings
- `search()`: Semantic search with similarity scoring
- `count()`: Get document count
- `reset()`: Clear collection

**Connections**:
- ← Used by: `rag_service` (local mode)
- ← Used by: `scripts/process_handbook.py` (indexing)
- → ChromaDB (persistent storage)

---

#### `app/services/embeddings.py` - **Embedding Service**
**Purpose**: Local embedding generation using sentence-transformers

**Responsibilities**:
- Loads embedding model
- Generates embeddings for text
- Supports multiple models (English, multilingual)

**Key Methods**:
- `encode()`: Generate embeddings for text list
- `encode_query()`: Generate single query embedding

**Connections**:
- ← Used by: `pdf_processor` (semantic chunking)
- → Sentence-transformers library
- → Model cache (local storage)

---

#### `app/services/pdf_processor.py` - **PDF Processing & Chunking**
**Purpose**: Extract text from PDF and chunk it using various strategies

**Responsibilities**:
- Extract text from PDF files
- Implement 4 chunking strategies:
  - **Sentence-based**: Split at sentence boundaries
  - **Semantic**: Group by similarity using embeddings
  - **Section-based**: Chunk by document sections
  - **Recursive**: Hierarchical splitting
- Extract document sections

**Key Methods**:
- `extract_text_from_pdf()`: PDF text extraction
- `chunk_text()`: Main chunking method (strategy selector)
- `_chunk_sentence_based()`: Sentence chunking
- `_chunk_semantic()`: Semantic chunking
- `_chunk_section_based()`: Section chunking
- `_chunk_recursive()`: Recursive chunking
- `extract_sections()`: Section detection

**Connections**:
- ← Used by: `scripts/process_handbook.py`
- → `embeddings` (for semantic chunking)
- → PDF libraries (pdfplumber, pypdf)

---

#### `app/services/conversation_memory.py` - **Conversation Memory**
**Purpose**: Manages conversation history for follow-up questions

**Responsibilities**:
- Store conversation history per conversation_id
- Retrieve conversation context
- Auto-expire old conversations (TTL)
- Limit history size

**Key Methods**:
- `create_conversation()`: Create new conversation
- `add_message()`: Store user/assistant message
- `get_history()`: Retrieve conversation history
- `get_context_string()`: Format history for prompts
- `clear_expired()`: Cleanup old conversations

**Connections**:
- ← Used by: `rag_service` (conversation context)
- → In-memory storage (dict)

---

#### `app/services/language_detector.py` - **Language Detection**
**Purpose**: Detect and validate student query language

**Responsibilities**:
- Detect language from text
- Validate supported languages
- Map language codes

**Key Methods**:
- `detect_language()`: Detect language code
- `is_supported()`: Check if language is supported
- `get_language_name()`: Get full language name

**Connections**:
- ← Used by: `rag_service`
- → langdetect library

---

#### `app/services/azure_search.py` - **Azure AI Search** (Production)
**Purpose**: Azure AI Search integration for production mode

**Responsibilities**:
- Connect to Azure AI Search service
- Perform semantic search
- Handle language-specific queries

**Connections**:
- ← Used by: `rag_service` (Azure mode only)
- → Azure AI Search API

---

#### `app/services/mock_openai.py` - **Mock OpenAI** (Local Mode)
**Purpose**: Rule-based response generation for local testing

**Responsibilities**:
- Generate responses without API calls
- Use rule-based logic
- Extract context from prompts

**Connections**:
- ← Used by: `rag_service` (local mode only)

---

### 📜 Script Files

#### `scripts/process_handbook.py` - **PDF Processing Script**
**Purpose**: Process ICL handbook PDF and populate vector database

**Responsibilities**:
- Download PDF from URL (or use local file)
- Extract text using PDF processor
- Chunk text using selected strategy
- Generate embeddings and store in vector DB

**Connections**:
- → `pdf_processor` (text extraction & chunking)
- → `vector_store` (document storage)
- → `embeddings` (if semantic chunking)

**Usage**:
```bash
python scripts/process_handbook.py --strategy semantic
```

---

#### `scripts/test_local.py` - **API Testing Script**
**Purpose**: Test the API locally

**Responsibilities**:
- Send test queries to API
- Display responses
- Test health endpoint

**Connections**:
- → HTTP requests to `app.main`

---

#### `scripts/deploy_azure.py` - **Azure Deployment**
**Purpose**: Automate Azure resource creation

**Responsibilities**:
- Create resource group
- Create Azure AI Search (Free tier)
- Create Azure OpenAI (S0 tier)
- Create Container Registry
- Create App Service Plan

**Connections**:
- → Azure CLI commands

---

#### `scripts/destroy_azure.py` - **Azure Cleanup**
**Purpose**: Delete all Azure resources

**Responsibilities**:
- Delete resource group and all resources
- Safety confirmation

**Connections**:
- → Azure CLI commands

---

## 📚 API Documentation & Testing

### Swagger UI

The application includes **interactive Swagger UI** for testing and documentation:

**Access Points**:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

**Features**:
- ✅ Interactive API testing ("Try it out" functionality)
- ✅ Request/response examples
- ✅ Schema validation
- ✅ Authentication support
- ✅ Error response examples
- ✅ Field descriptions and constraints

**Usage**:
1. Start server: `python -m app.main`
2. Open browser: http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Fill in request body
5. Click "Execute"
6. View response

**Configuration**:
- Swagger UI is automatically enabled in FastAPI
- Tags and metadata defined in `app/openapi_tags.py`
- Endpoint descriptions from docstrings
- Request/response models from `app/models.py`

See [RUN_SWAGGER_LOCALLY.md](RUN_SWAGGER_LOCALLY.md) for detailed testing guide.

---

## 🔄 Data Flow Diagram

### Request Flow (Local Mode)

```
┌─────────────┐
│   Student   │
│  (WhatsApp) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     n8n     │  HTTP POST /api/v1/query
│  Workflow   │  {query, conversation_id}
└──────┬──────┘
       │
       ├─────────────────────────────┐
       │                             │
       ▼                             ▼
┌─────────────┐            ┌──────────────────┐
│  Swagger UI │            │  app/main.py     │
│  (Testing)  │            │  • FastAPI       │
│  /docs      │            │  • Swagger UI    │
└─────────────┘            │  • API key auth  │
                           │  • Validation    │
                           └──────┬───────────┘
                                  │
                                  ▼
       │
       ▼
┌─────────────────────────────────────────┐
│    app/services/rag_service.py         │
│  • Conversation memory retrieval       │
│  • Language detection                   │
│  • Query processing                     │
└──────┬──────────────────────────────────┘
       │
       ├─────────────────┐
       ▼                 ▼
┌──────────────┐  ┌──────────────────────┐
│ conversation │  │  vector_store.py     │
│   _memory    │  │  • Semantic search   │
│              │  │  • ChromaDB query    │
└──────┬───────┘  └──────┬───────────────┘
       │                 │
       │                 ▼
       │          ┌──────────────┐
       │          │  Search      │
       │          │  Results     │
       │          └──────┬───────┘
       │                 │
       ▼                 ▼
┌─────────────────────────────────────────┐
│    rag_service.py (continued)            │
│  • Build context from results           │
│  • Add conversation history             │
│  • Generate response                    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│    mock_openai.py                       │
│  • Rule-based response generation       │
│  • Context-aware answers                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│    rag_service.py (final)                │
│  • Apply guardrails                     │
│  • Store in conversation memory         │
│  • Calculate confidence                 │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│    app/main.py                          │
│  • Format response                      │
│  • Return JSON                          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Student   │
│  Response   │
└─────────────┘
```

### PDF Processing Flow

```
┌─────────────────────────┐
│  ICL Handbook PDF       │
│  (URL or local file)    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  scripts/process_handbook.py            │
│  • Download PDF (if URL)                │
│  • Initialize services                  │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  app/services/pdf_processor.py         │
│  • Extract text from PDF                │
│  • Chunk using selected strategy        │
│    - Sentence/Semantic/Section/Recursive│
└──────────┬──────────────────────────────┘
           │
           ├─────────────────┐
           ▼                 ▼
┌──────────────┐    ┌──────────────────┐
│  embeddings  │    │  Text Chunks     │
│  (if semantic)│    │  with metadata   │
└──────────────┘    └────────┬─────────┘
                            │
                            ▼
┌─────────────────────────────────────────┐
│  app/services/vector_store.py           │
│  • Add documents to ChromaDB            │
│  • Generate embeddings (auto)           │
│  • Store with metadata                  │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│  ChromaDB Database      │
│  (./chroma_db/)         │
│  • Persistent storage    │
│  • Ready for queries     │
└─────────────────────────┘
```

---

## 🔗 Component Relationships

### Dependency Graph

```
app/main.py
  ├── app/config.py (settings)
  ├── app/models.py (QueryRequest, QueryResponse)
  └── app/services/rag_service.py
        ├── app/config.py (settings)
        ├── app/services/conversation_memory.py
        ├── app/services/language_detector.py
        ├── app/services/vector_store.py (local mode)
        │     └── app/config.py (vector_db_path)
        ├── app/services/azure_search.py (Azure mode)
        ├── app/services/mock_openai.py (local mode)
        └── Semantic Kernel (Azure mode)

scripts/process_handbook.py
  ├── app/services/pdf_processor.py
  │     ├── app/services/embeddings.py (semantic chunking)
  │     └── PDF libraries (pdfplumber, pypdf)
  ├── app/services/vector_store.py
  └── app/config.py (chunking_strategy)
```

---

## 🎯 Key Design Patterns

### 1. **Strategy Pattern** (Chunking)
- `pdf_processor.chunk_text()` selects strategy dynamically
- Four implementations: sentence, semantic, section, recursive
- Configurable via environment variable

### 2. **Factory Pattern** (Mode Selection)
- `rag_service` creates different services based on mode
- Local mode: vector_store + mock_openai
- Azure mode: azure_search + Semantic Kernel

### 3. **Singleton Pattern** (Services)
- `rag_service` initialized once in `main.py`
- `conversation_memory` uses global instance
- `settings` is a singleton configuration

### 4. **Repository Pattern** (Vector Store)
- `vector_store` abstracts ChromaDB operations
- Provides clean interface for document operations

---

## 🔄 Request Lifecycle

1. **Request Arrives** → `app/main.py` receives HTTP POST
2. **Authentication** → `verify_api_key()` validates API key
3. **Validation** → Pydantic validates `QueryRequest` model
4. **RAG Processing** → `rag_service.process_query()` called
5. **Memory Check** → Retrieve conversation history if `conversation_id` provided
6. **Language Detection** → Detect or validate query language
7. **Vector Search** → Search ChromaDB for relevant documents
8. **Context Building** → Combine search results + conversation history
9. **Response Generation** → Generate answer using mock OpenAI or Semantic Kernel
10. **Guardrails** → Validate and filter response
11. **Memory Storage** → Store Q&A in conversation memory
12. **Response** → Return `QueryResponse` with answer and metadata

---

## 🗄️ Data Storage

### Local Mode
- **ChromaDB**: Vector database (`./chroma_db/`)
  - Stores document chunks with embeddings
  - Persistent across restarts
- **In-Memory**: Conversation memory
  - Dictionary: `{conversation_id: [messages]}`
  - Lost on restart (TTL: 24 hours)

### Azure Mode
- **Azure AI Search**: Document index
- **Azure OpenAI**: Response generation
- **In-Memory**: Conversation memory (same as local)

---

## 🚀 Execution Modes

### Local Mode (`MODE=local`)
- Uses ChromaDB for vector search
- Uses mock OpenAI for responses
- No external API calls
- Perfect for development/testing

### Azure Mode (`MODE=azure`)
- Uses Azure AI Search
- Uses Azure OpenAI with Semantic Kernel
- Production-ready
- Requires Azure credentials

---

## 📊 Configuration Flow

```
.env file
  │
  ▼
app/config.py (Settings class)
  │
  ├──→ Mode detection (local/azure)
  ├──→ Chunking strategy
  ├──→ Memory settings
  └──→ Service credentials
        │
        ▼
  All service files
```

---

## 🔐 Security Flow

```
HTTP Request
  │
  ▼
API Key Header (X-API-Key)
  │
  ▼
verify_api_key() in main.py
  │
  ├──→ Check settings.api_key
  ├──→ Compare with header
  └──→ Allow/Deny request
```

---

This architecture provides:
- ✅ **Separation of Concerns**: Each file has a single responsibility
- ✅ **Modularity**: Services can be swapped (local vs Azure)
- ✅ **Testability**: Components are isolated and testable
- ✅ **Scalability**: Can switch from local to Azure seamlessly
- ✅ **Maintainability**: Clear structure and dependencies
