# Production Architecture - Azure & Docker Implementation

Complete architecture diagrams for production deployment using Azure services and Docker containers.

## 🏗️ Production System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Student[👤 Student<br/>WhatsApp]
        Admin[👨‍💼 Admin<br/>Dashboard]
    end
    
    subgraph "Integration Layer"
        n8n[n8n Workflow<br/>Automation Platform]
        Webhook[Webhook<br/>Endpoint]
    end
    
    subgraph "Azure Application Gateway"
        Gateway[Application Gateway<br/>Load Balancer<br/>SSL Termination]
    end
    
    subgraph "Azure App Service"
        AppService[App Service<br/>Container Host]
        subgraph "Docker Container"
            FastAPI[FastAPI Application<br/>Python 3.10+<br/>Port 8000]
            Gunicorn[Gunicorn<br/>WSGI Server]
        end
    end
    
    subgraph "Azure AI Services"
        AzureSearch[Azure AI Search<br/>Vector Database<br/>Semantic Search]
        AzureOpenAI[Azure OpenAI<br/>GPT-4 Deployment<br/>Semantic Kernel]
    end
    
    subgraph "Azure Storage"
        ACR[Azure Container Registry<br/>Docker Images]
        BlobStorage[Blob Storage<br/>PDF Documents<br/>Knowledge Base]
    end
    
    subgraph "Azure Monitoring"
        AppInsights[Application Insights<br/>Logging & Metrics]
        LogAnalytics[Log Analytics<br/>Centralized Logs]
    end
    
    subgraph "Azure Security"
        KeyVault[Key Vault<br/>Secrets Management]
        ManagedIdentity[Managed Identity<br/>Service Authentication]
    end
    
    subgraph "CI/CD Pipeline"
        GitHub[GitHub Repository]
        GitHubActions[GitHub Actions<br/>CI/CD Workflow]
        Build[Build Docker Image]
        Push[Push to ACR]
        Deploy[Deploy to App Service]
    end
    
    Student -->|HTTP/HTTPS| n8n
    Admin -->|HTTPS| Gateway
    n8n -->|API Calls| Gateway
    Webhook -->|POST /api/v1/query| Gateway
    
    Gateway -->|Route Traffic| AppService
    AppService -->|Runs| FastAPI
    FastAPI -->|WSGI| Gunicorn
    
    FastAPI -->|Query| AzureSearch
    FastAPI -->|Generate Response| AzureOpenAI
    FastAPI -->|Read Secrets| KeyVault
    FastAPI -->|Authenticate| ManagedIdentity
    
    AzureSearch -->|Index Documents| BlobStorage
    FastAPI -->|Logs| AppInsights
    AppInsights -->|Store Logs| LogAnalytics
    
    GitHub -->|Trigger| GitHubActions
    GitHubActions -->|Build| Build
    Build -->|Push| ACR
    ACR -->|Pull Image| AppService
    GitHubActions -->|Deploy| Deploy
    Deploy -->|Update| AppService
    
    style FastAPI fill:#4CAF50
    style AzureSearch fill:#0078D4
    style AzureOpenAI fill:#0078D4
    style AppService fill:#0078D4
    style ACR fill:#0078D4
```

## 🐳 Docker Container Architecture

```mermaid
graph TB
    subgraph "Docker Image Layers"
        Base[Python 3.10 Slim<br/>Base Image]
        Dependencies[Install Dependencies<br/>requirements.txt]
        AppCode[Copy Application Code<br/>app/ directory]
        Scripts[Copy Scripts<br/>scripts/ directory]
        Config[Copy Config Files<br/>.env, Dockerfile]
    end
    
    subgraph "Container Runtime"
        Container[Docker Container<br/>Running Instance]
        subgraph "Application Process"
            Gunicorn[Gunicorn Master<br/>Process Manager]
            Workers[Gunicorn Workers<br/>4-8 Workers]
            FastAPI[FastAPI App<br/>Per Worker]
        end
        HealthCheck[Health Check<br/>/health endpoint]
    end
    
    subgraph "Container Resources"
        Volumes[Volume Mounts<br/>Optional: Local Data]
        Network[Network Bridge<br/>Port 8000]
        Environment[Environment Variables<br/>From Azure App Service]
    end
    
    Base --> Dependencies
    Dependencies --> AppCode
    AppCode --> Scripts
    Scripts --> Config
    
    Config --> Container
    Container --> Gunicorn
    Gunicorn --> Workers
    Workers --> FastAPI
    Container --> HealthCheck
    
    Container --> Volumes
    Container --> Network
    Container --> Environment
    
    style Container fill:#0db7ed
    style Gunicorn fill:#4CAF50
    style FastAPI fill:#009688
```

## 🔄 Production Data Flow

```mermaid
sequenceDiagram
    participant Student
    participant n8n
    participant Gateway as App Gateway
    participant AppService as App Service
    participant Container as Docker Container
    participant FastAPI as FastAPI App
    participant AzureSearch as Azure AI Search
    participant AzureOpenAI as Azure OpenAI
    participant KeyVault as Key Vault
    participant AppInsights as App Insights
    
    Student->>n8n: Ask Question (WhatsApp)
    n8n->>Gateway: POST /api/v1/query<br/>{query, conversation_id}
    Gateway->>Gateway: SSL Termination<br/>Load Balancing
    Gateway->>AppService: Route to Container
    AppService->>Container: Forward Request
    Container->>FastAPI: Process Request
    
    FastAPI->>KeyVault: Get API Keys<br/>(Cached)
    KeyVault-->>FastAPI: Return Secrets
    
    FastAPI->>FastAPI: Validate Request<br/>Check API Key
    
    FastAPI->>AzureSearch: Semantic Search<br/>Query: student question
    AzureSearch-->>FastAPI: Relevant Documents
    
    FastAPI->>AzureOpenAI: Generate Response<br/>Context + Documents
    AzureOpenAI-->>FastAPI: AI Response
    
    FastAPI->>FastAPI: Apply Guardrails<br/>Validate Response
    
    FastAPI->>AppInsights: Log Request<br/>Metrics & Telemetry
    FastAPI-->>Container: JSON Response
    Container-->>AppService: Return Response
    AppService-->>Gateway: Forward Response
    Gateway-->>n8n: JSON Response
    n8n-->>Student: Answer (WhatsApp)
```

## 🚀 Deployment Pipeline

```mermaid
graph LR
    subgraph "Source Control"
        Dev[Developer<br/>Local Development]
        GitHub[GitHub Repository<br/>Main Branch]
    end
    
    subgraph "CI/CD Pipeline"
        Trigger[Git Push<br/>Triggers Workflow]
        Build[Build Stage<br/>Docker Build]
        Test[Test Stage<br/>Unit Tests]
        Security[Security Scan<br/>Vulnerability Check]
        Push[Push to ACR<br/>Tag with Version]
    end
    
    subgraph "Azure Container Registry"
        ACR[ACR Repository<br/>rag-student-support:latest<br/>rag-student-support:v1.0.0]
    end
    
    subgraph "Azure Deployment"
        AppService[App Service<br/>Pull from ACR]
        Staging[Staging Slot<br/>Blue-Green Deploy]
        Production[Production Slot<br/>Live Traffic]
    end
    
    subgraph "Monitoring"
        HealthCheck[Health Check<br/>/health endpoint]
        Rollback[Auto Rollback<br/>If Unhealthy]
    end
    
    Dev -->|git push| GitHub
    GitHub -->|Webhook| Trigger
    Trigger --> Build
    Build --> Test
    Test --> Security
    Security --> Push
    Push --> ACR
    
    ACR -->|Pull Image| AppService
    AppService -->|Deploy to| Staging
    Staging -->|Health Check| HealthCheck
    HealthCheck -->|Pass| Production
    HealthCheck -->|Fail| Rollback
    Rollback -->|Revert to| ACR
    
    style GitHub fill:#24292e
    style ACR fill:#0078D4
    style AppService fill:#0078D4
    style Production fill:#4CAF50
```

## 🔐 Security Architecture

```mermaid
graph TB
    subgraph "Network Security"
        VNet[Virtual Network<br/>Isolated Network]
        NSG[Network Security Group<br/>Firewall Rules]
        PrivateEndpoint[Private Endpoints<br/>Secure Connections]
    end
    
    subgraph "Identity & Access"
        ManagedIdentity[Managed Identity<br/>No Secrets in Code]
        RBAC[Role-Based Access Control<br/>Azure AD]
        APIKey[API Key Authentication<br/>X-API-Key Header]
    end
    
    subgraph "Secrets Management"
        KeyVault[Azure Key Vault<br/>Centralized Secrets]
        Secrets[Stored Secrets:<br/>- Azure Search Key<br/>- OpenAI Key<br/>- API Keys]
    end
    
    subgraph "Data Security"
        Encryption[Encryption at Rest<br/>Azure Storage]
        TLS[TLS 1.2+<br/>In Transit]
        Firewall[Azure Search Firewall<br/>IP Whitelist]
    end
    
    subgraph "Application Security"
        ContainerScan[Container Scanning<br/>Vulnerability Check]
        DDoS[DDoS Protection<br/>Application Gateway]
        WAF[Web Application Firewall<br/>OWASP Rules]
    end
    
    VNet --> NSG
    VNet --> PrivateEndpoint
    AppService --> ManagedIdentity
    ManagedIdentity --> KeyVault
    KeyVault --> Secrets
    
    AppService --> TLS
    AzureSearch --> Encryption
    AzureSearch --> Firewall
    
    Gateway --> DDoS
    Gateway --> WAF
    Container --> ContainerScan
    
    style KeyVault fill:#FF6B6B
    style ManagedIdentity fill:#4ECDC4
    style TLS fill:#95E1D3
```

## 📊 Monitoring & Observability

```mermaid
graph TB
    subgraph "Application Layer"
        FastAPI[FastAPI Application]
        Logs[Application Logs<br/>Structured Logging]
        Metrics[Custom Metrics<br/>Request Count, Latency]
    end
    
    subgraph "Azure Monitoring"
        AppInsights[Application Insights<br/>APM & Telemetry]
        LogAnalytics[Log Analytics Workspace<br/>Centralized Logs]
        Alerts[Alert Rules<br/>Threshold-based]
    end
    
    subgraph "Dashboards"
        Dashboard[Azure Dashboard<br/>Real-time Metrics]
        Grafana[Grafana Dashboard<br/>Optional]
    end
    
    subgraph "Notifications"
        Email[Email Alerts]
        Teams[Microsoft Teams<br/>Notifications]
        SMS[SMS Alerts<br/>Critical Issues]
    end
    
    FastAPI --> Logs
    FastAPI --> Metrics
    Logs --> AppInsights
    Metrics --> AppInsights
    AppInsights --> LogAnalytics
    AppInsights --> Alerts
    AppInsights --> Dashboard
    
    Alerts --> Email
    Alerts --> Teams
    Alerts --> SMS
    
    LogAnalytics --> Grafana
    
    style AppInsights fill:#0078D4
    style Dashboard fill:#4CAF50
    style Alerts fill:#FF9800
```

## 🔄 Scaling Architecture

```mermaid
graph TB
    subgraph "Auto-Scaling"
        Metrics[Performance Metrics<br/>CPU, Memory, Requests]
        ScaleRules[Scale Rules<br/>Threshold-based]
        ScaleOut[Scale Out<br/>Add Instances]
        ScaleIn[Scale In<br/>Remove Instances]
    end
    
    subgraph "App Service Plan"
        Plan[App Service Plan<br/>Standard/Premium]
        Instances1[Instance 1<br/>Container]
        Instances2[Instance 2<br/>Container]
        Instances3[Instance N<br/>Container]
    end
    
    subgraph "Load Distribution"
        LoadBalancer[Load Balancer<br/>Round Robin]
        HealthCheck[Health Checks<br/>Per Instance]
    end
    
    Metrics --> ScaleRules
    ScaleRules -->|High Load| ScaleOut
    ScaleRules -->|Low Load| ScaleIn
    
    ScaleOut --> Instances1
    ScaleOut --> Instances2
    ScaleOut --> Instances3
    
    Instances1 --> LoadBalancer
    Instances2 --> LoadBalancer
    Instances3 --> LoadBalancer
    
    LoadBalancer --> HealthCheck
    HealthCheck -->|Healthy| Instances1
    HealthCheck -->|Healthy| Instances2
    HealthCheck -->|Unhealthy| ScaleIn
    
    style ScaleOut fill:#4CAF50
    style ScaleIn fill:#FF9800
    style LoadBalancer fill:#2196F3
```

## 🗄️ Data Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        PDF[ICL Handbook PDF<br/>Source Document]
        Updates[Document Updates<br/>Periodic Refresh]
    end
    
    subgraph "Processing Pipeline"
        Processor[PDF Processor<br/>Extract & Chunk]
        Embeddings[Generate Embeddings<br/>Azure OpenAI]
        Indexer[Index Documents<br/>Azure AI Search]
    end
    
    subgraph "Azure AI Search"
        Index[Search Index<br/>Vector + Metadata]
        Fields[Index Fields:<br/>- content<br/>- embedding<br/>- metadata<br/>- source]
    end
    
    subgraph "Query Flow"
        Query[Student Query]
        Search[Semantic Search<br/>Vector Similarity]
        Results[Ranked Results<br/>Top K Documents]
    end
    
    PDF --> Processor
    Updates --> Processor
    Processor --> Embeddings
    Embeddings --> Indexer
    Indexer --> Index
    Index --> Fields
    
    Query --> Search
    Search --> Index
    Index --> Results
    
    style Index fill:#0078D4
    style Embeddings fill:#4CAF50
```

## 🌐 Network Architecture

```mermaid
graph TB
    subgraph "Internet"
        Users[End Users<br/>Students, n8n]
    end
    
    subgraph "Azure Edge"
        CDN[Azure CDN<br/>Optional: Static Assets]
        Gateway[Application Gateway<br/>Public IP]
    end
    
    subgraph "Azure Network"
        VNet[Virtual Network<br/>10.0.0.0/16]
        Subnet1[App Service Subnet<br/>10.0.1.0/24]
        Subnet2[Private Endpoint Subnet<br/>10.0.2.0/24]
    end
    
    subgraph "Azure Services"
        AppService[App Service<br/>Private Endpoint]
        AzureSearch[Azure AI Search<br/>Private Endpoint]
        AzureOpenAI[Azure OpenAI<br/>Private Endpoint]
    end
    
    Users -->|HTTPS| CDN
    Users -->|HTTPS| Gateway
    Gateway -->|Route| VNet
    VNet --> Subnet1
    VNet --> Subnet2
    
    Subnet1 --> AppService
    Subnet2 --> AzureSearch
    Subnet2 --> AzureOpenAI
    
    AppService -.->|Private Link| AzureSearch
    AppService -.->|Private Link| AzureOpenAI
    
    style VNet fill:#0078D4
    style Gateway fill:#4CAF50
    style PrivateEndpoint fill:#FF6B6B
```

## 📋 Component Summary

### Azure Services Used

| Service | Purpose | Tier |
|---------|---------|------|
| **App Service** | Container hosting | Standard/Premium |
| **Azure AI Search** | Vector database & semantic search | Standard S1 |
| **Azure OpenAI** | LLM for response generation | Pay-per-use |
| **Container Registry** | Docker image storage | Basic |
| **Application Gateway** | Load balancer & SSL | Standard |
| **Key Vault** | Secrets management | Standard |
| **Application Insights** | Monitoring & logging | Pay-per-use |
| **Log Analytics** | Centralized logs | Pay-per-use |
| **Blob Storage** | Document storage | Hot tier |

### Docker Configuration

- **Base Image**: Python 3.10-slim
- **WSGI Server**: Gunicorn with 4-8 workers
- **Port**: 8000 (internal)
- **Health Check**: `/health` endpoint
- **Multi-stage Build**: Optimized image size

### High Availability

- **Multi-region**: Deploy to multiple Azure regions
- **Auto-scaling**: Based on CPU, memory, requests
- **Health Checks**: Automatic instance replacement
- **Backup**: Regular container image backups
- **Disaster Recovery**: Cross-region replication

---

## 🎯 Key Production Features

✅ **Scalability**: Auto-scaling based on load  
✅ **Security**: Private endpoints, Key Vault, managed identity  
✅ **Monitoring**: Application Insights, Log Analytics  
✅ **CI/CD**: Automated deployment pipeline  
✅ **High Availability**: Multi-instance, health checks  
✅ **Performance**: CDN, load balancing, caching  
✅ **Compliance**: Encryption, audit logs, RBAC  
