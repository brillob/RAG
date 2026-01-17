# Application Architecture Diagrams

Visual representation of the RAG Student Support System architecture.

## 🏗️ System Architecture Overview

```mermaid
graph TB
    subgraph "External Systems"
        Student[👤 Student<br/>WhatsApp]
        n8n[n8n Workflow<br/>Automation]
        Swagger[🌐 Swagger UI<br/>Interactive Testing]
    end
    
    subgraph "API Layer"
        Main[app/main.py<br/>FastAPI Server<br/>+ Swagger UI]
        Auth[API Key<br/>Verification]
        Docs[OpenAPI<br/>Documentation]
    end
    
    subgraph "Core Services"
        RAG[app/services/rag_service.py<br/>RAG Orchestrator]
        Memory[app/services/conversation_memory.py<br/>Conversation Memory]
        LangDetect[app/services/language_detector.py<br/>Language Detection]
    end
    
    subgraph "Local Mode Services"
        VectorDB[app/services/vector_store.py<br/>ChromaDB]
        MockAI[app/services/mock_openai.py<br/>Mock OpenAI]
    end
    
    subgraph "Azure Mode Services"
        AzureSearch[app/services/azure_search.py<br/>Azure AI Search]
        SemanticKernel[Semantic Kernel<br/>Azure OpenAI]
    end
    
    subgraph "Data Storage"
        ChromaDB[(ChromaDB<br/>Vector Database)]
        MemoryStore[(In-Memory<br/>Conversation History)]
        AzureServices[(Azure Services<br/>Search + OpenAI)]
    end
    
    subgraph "Configuration"
        Config[app/config.py<br/>Settings]
        Models[app/models.py<br/>Data Models]
    end
    
    Student -->|HTTP Request| n8n
    n8n -->|POST /api/v1/query| Main
    Swagger -->|Interactive Testing| Main
    Main -->|Validate| Auth
    Main -->|Serves| Docs
    Auth -->|Process| RAG
    
    RAG -->|Get History| Memory
    RAG -->|Detect Language| LangDetect
    RAG -->|Mode Check| Config
    
    Config -->|local| VectorDB
    Config -->|azure| AzureSearch
    
    VectorDB -->|Search| ChromaDB
    VectorDB -->|Read| ChromaDB
    Memory -->|Store/Retrieve| MemoryStore
    
    RAG -->|Local Mode| MockAI
    RAG -->|Azure Mode| SemanticKernel
    
    AzureSearch -->|Query| AzureServices
    SemanticKernel -->|Generate| AzureServices
    
    RAG -->|Response| Main
    Main -->|JSON Response| n8n
    n8n -->|WhatsApp| Student
    
    Config -.->|Configures| RAG
    Config -.->|Configures| VectorDB
    Config -.->|Configures| Memory
    Models -.->|Validates| Main
```

## 📄 PDF Processing Flow

```mermaid
graph LR
    subgraph "Input"
        PDF[ICL Handbook PDF<br/>URL or File]
    end
    
    subgraph "Processing Script"
        Script[scripts/process_handbook.py<br/>Main Script]
        PDFProc[app/services/pdf_processor.py<br/>PDF Processor]
        Embed[app/services/embeddings.py<br/>Embeddings]
    end
    
    subgraph "Chunking Strategies"
        Sentence[Sentence-Based<br/>Split by sentences]
        Semantic[Semantic<br/>Group by similarity]
        Section[Section-Based<br/>Split by sections]
        Recursive[Recursive<br/>Hierarchical split]
    end
    
    subgraph "Storage"
        VectorStore[app/services/vector_store.py<br/>Vector Store]
        DB[(ChromaDB<br/>./chroma_db/)]
    end
    
    PDF -->|Download/Read| Script
    Script -->|Extract Text| PDFProc
    PDFProc -->|Select Strategy| Sentence
    PDFProc -->|Select Strategy| Semantic
    PDFProc -->|Select Strategy| Section
    PDFProc -->|Select Strategy| Recursive
    
    Semantic -->|Needs Embeddings| Embed
    Sentence -->|Chunks| VectorStore
    Semantic -->|Chunks| VectorStore
    Section -->|Chunks| VectorStore
    Recursive -->|Chunks| VectorStore
    
    VectorStore -->|Store with Embeddings| DB
```

## 🔄 Query Processing Flow (Detailed)

```mermaid
sequenceDiagram
    participant Student
    participant n8n
    participant Main as main.py
    participant RAG as rag_service.py
    participant Memory as conversation_memory.py
    participant LangDetect as language_detector.py
    participant VectorDB as vector_store.py
    participant ChromaDB as ChromaDB
    participant MockAI as mock_openai.py
    
    Student->>n8n: Ask Question (WhatsApp)
    n8n->>Main: POST /api/v1/query<br/>{query, conversation_id}
    Main->>Main: Verify API Key
    Main->>RAG: process_query(query, conversation_id)
    
    alt conversation_id exists
        RAG->>Memory: get_history(conversation_id)
        Memory-->>RAG: Conversation context
    else new conversation
        RAG->>Memory: create_conversation()
        Memory-->>RAG: New conversation_id
    end
    
    RAG->>Memory: add_message(user, query)
    RAG->>LangDetect: detect_language(query)
    LangDetect-->>RAG: Language code (e.g., "en")
    
    RAG->>VectorDB: search(query, n_results=5)
    VectorDB->>ChromaDB: Query embeddings
    ChromaDB-->>VectorDB: Similar documents
    VectorDB-->>RAG: Search results
    
    RAG->>RAG: build_context(results + history)
    RAG->>MockAI: generate_response(query, context)
    MockAI-->>RAG: Generated response
    
    RAG->>RAG: apply_guardrails(response)
    RAG->>Memory: add_message(assistant, response)
    RAG-->>Main: {response, confidence, sources, conversation_id}
    Main-->>n8n: JSON Response
    n8n-->>Student: Answer (WhatsApp)
```

## 🧩 Component Interaction Diagram

```mermaid
graph TB
    subgraph "Request Layer"
        API[FastAPI Endpoints]
    end
    
    subgraph "Orchestration Layer"
        RAG[RAG Service<br/>Orchestrator]
    end
    
    subgraph "Support Services"
        Memory[Conversation<br/>Memory]
        Lang[Language<br/>Detector]
    end
    
    subgraph "Search Layer"
        VectorStore[Vector Store<br/>ChromaDB Wrapper]
        AzureSearch[Azure Search<br/>Production]
    end
    
    subgraph "Generation Layer"
        MockAI[Mock OpenAI<br/>Local]
        SemanticKernel[Semantic Kernel<br/>Azure]
    end
    
    subgraph "Data Layer"
        ChromaDB[(ChromaDB)]
        Azure[(Azure Services)]
        MemStore[(Memory Store)]
    end
    
    API -->|1. Process Query| RAG
    RAG -->|2. Get History| Memory
    RAG -->|3. Detect Language| Lang
    RAG -->|4. Search| VectorStore
    RAG -->|5. Search| AzureSearch
    RAG -->|6. Generate| MockAI
    RAG -->|7. Generate| SemanticKernel
    
    Memory -->|Read/Write| MemStore
    VectorStore -->|Query| ChromaDB
    AzureSearch -->|Query| Azure
    SemanticKernel -->|Generate| Azure
    
    RAG -->|8. Return Response| API
```

## 🔀 Mode Selection Flow

```mermaid
graph TD
    Start[Application Start] --> ReadConfig[Read .env file]
    ReadConfig --> CheckMode{Check MODE}
    
    CheckMode -->|MODE=local| LocalInit[Initialize Local Services]
    CheckMode -->|MODE=azure| AzureInit[Initialize Azure Services]
    
    LocalInit --> LocalVector[Vector Store<br/>ChromaDB]
    LocalInit --> LocalAI[Mock OpenAI]
    LocalInit --> LocalRAG[Configure RAG Service]
    
    AzureInit --> AzureSearch[Azure AI Search]
    AzureInit --> AzureOpenAI[Azure OpenAI<br/>Semantic Kernel]
    AzureInit --> AzureRAG[Configure RAG Service]
    
    LocalRAG --> Ready[Service Ready]
    AzureRAG --> Ready
    
    Ready --> WaitRequest[Wait for Requests]
    WaitRequest --> Process[Process Query]
    
    Process --> CheckMode2{Current Mode?}
    CheckMode2 -->|local| UseLocal[Use Vector Store + Mock AI]
    CheckMode2 -->|azure| UseAzure[Use Azure Search + Semantic Kernel]
    
    UseLocal --> Return[Return Response]
    UseAzure --> Return
```

## 📊 Chunking Strategy Flow

```mermaid
graph TD
    PDF[PDF Document] --> Extract[Extract Text]
    Extract --> SelectStrategy{Select Strategy<br/>from Config}
    
    SelectStrategy -->|sentence| Sentence[Sentence-Based<br/>Split at .!?]
    SelectStrategy -->|semantic| Semantic[Semantic<br/>Group by similarity]
    SelectStrategy -->|section| Section[Section-Based<br/>Split by headers]
    SelectStrategy -->|recursive| Recursive[Recursive<br/>Hierarchical]
    
    Sentence --> Chunks1[Text Chunks]
    Section --> Chunks2[Text Chunks]
    Recursive --> Chunks3[Text Chunks]
    
    Semantic --> Embed[Generate Embeddings]
    Embed --> Similarity[Calculate Similarity]
    Similarity --> Merge[Merge Similar Chunks]
    Merge --> Chunks4[Text Chunks]
    
    Chunks1 --> Metadata[Add Metadata]
    Chunks2 --> Metadata
    Chunks3 --> Metadata
    Chunks4 --> Metadata
    
    Metadata --> Store[Store in Vector DB]
    Store --> Ready[Ready for Search]
```

## 💾 Memory Management Flow

```mermaid
stateDiagram-v2
    [*] --> NewQuery: Student asks question
    
    NewQuery --> CheckConvID: Receive query
    
    CheckConvID --> CreateNew: No conversation_id
    CheckConvID --> RetrieveExisting: Has conversation_id
    
    CreateNew --> StoreUserMsg: Create conversation
    RetrieveExisting --> CheckExpired: Get history
    
    CheckExpired --> CreateNew: Expired
    CheckExpired --> StoreUserMsg: Valid
    
    StoreUserMsg --> ProcessQuery: Store user message
    
    ProcessQuery --> GenerateResponse: Process with context
    
    GenerateResponse --> StoreAssistantMsg: Generate answer
    
    StoreAssistantMsg --> CheckLimit: Store assistant message
    
    CheckLimit --> TrimHistory: Exceeds max_history
    CheckLimit --> ReturnResponse: Within limit
    
    TrimHistory --> ReturnResponse: Keep last N messages
    
    ReturnResponse --> [*]: Return to student
    
    note right of CheckExpired
        TTL: 24 hours
        Auto-cleanup expired
    end note
    
    note right of CheckLimit
        Default: 10 messages
        Keep most recent
    end note
```

## 🔐 Security & Authentication Flow

```mermaid
graph LR
    Request[HTTP Request] --> Header{Has X-API-Key<br/>Header?}
    
    Header -->|No| CheckConfig{API Key<br/>Configured?}
    Header -->|Yes| ValidateKey[Validate Key]
    
    CheckConfig -->|No| Allow[Allow Request<br/>Dev Mode]
    CheckConfig -->|Yes| Reject[Reject Request<br/>401 Unauthorized]
    
    ValidateKey --> Match{Key Matches?}
    Match -->|Yes| Allow
    Match -->|No| Reject
    
    Allow --> Process[Process Query]
    Reject --> Error[Return 401 Error]
```

## 📦 Data Models Relationship

```mermaid
classDiagram
    class QueryRequest {
        +str query
        +Optional[str] student_id
        +Optional[str] language
        +Optional[str] conversation_id
    }
    
    class QueryResponse {
        +str response
        +str language
        +float confidence
        +List[str] sources
        +Optional[str] query_id
        +Optional[str] conversation_id
    }
    
    class HealthResponse {
        +str status
        +str version
    }
    
    class Settings {
        +str mode
        +str chunking_strategy
        +bool enable_conversation_memory
        +int max_conversation_history
        +str vector_db_path
        +Optional[str] azure_search_endpoint
        +Optional[str] azure_openai_endpoint
    }
    
    QueryRequest --> QueryResponse : transforms to
    Settings --> QueryRequest : validates
    Settings --> QueryResponse : configures
```

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        Local[Local Development<br/>Python + ChromaDB]
    end
    
    subgraph "Container"
        Docker[Docker Container<br/>Dockerfile]
        Compose[Docker Compose<br/>docker-compose.yml]
    end
    
    subgraph "Azure Production"
        ACR[Azure Container Registry]
        AKS[Azure Kubernetes Service]
        AppService[App Service]
        SearchSvc[Azure AI Search]
        OpenAISvc[Azure OpenAI]
    end
    
    Local -->|Build| Docker
    Docker -->|Push| ACR
    ACR -->|Deploy| AKS
    ACR -->|Deploy| AppService
    
    AppService -->|Query| SearchSvc
    AppService -->|Generate| OpenAISvc
    
    Compose -->|Local Testing| Local
```

---

## 📝 Legend

- **Solid Arrow (→)**: Direct call/usage
- **Dashed Arrow (-.->)**: Configuration/dependency
- **Box with rounded corners**: Service/Component
- **Box with sharp corners**: File/Module
- **Cylinder**: Database/Storage
- **Diamond**: Decision point
- **Parallelogram**: Input/Output

---

## 🎯 Key Takeaways

1. **Modular Design**: Each component has a single responsibility
2. **Mode Flexibility**: Seamless switching between local and Azure
3. **Memory Management**: Conversation context for follow-up questions
4. **Strategy Pattern**: Configurable chunking strategies
5. **Separation of Concerns**: Clear boundaries between layers
6. **Scalability**: Can scale from local testing to production Azure
