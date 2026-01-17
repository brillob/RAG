# Project Summary

## Overview

Complete multilingual RAG (Retrieval-Augmented Generation) system for student support with:
- ✅ **Local testing** with in-memory mock services (no Azure required)
- ✅ **Automated Azure deployment** with cost-optimized resource creation
- ✅ **Easy cleanup** with resource group deletion script

## Project Structure

```
RAG/
├── app/                          # Main application
│   ├── main.py                   # FastAPI server
│   ├── config.py                 # Configuration (supports local/azure modes)
│   ├── models.py                 # API models
│   └── services/
│       ├── rag_service.py         # Main RAG orchestration
│       ├── azure_search.py       # Azure AI Search integration
│       ├── mock_search.py        # In-memory search for local testing
│       ├── mock_openai.py        # Mock OpenAI for local testing
│       └── language_detector.py  # Multilingual support
│
├── scripts/
│   ├── deploy_azure.py            # Automated Azure deployment
│   ├── destroy_azure.py          # Delete all Azure resources
│   ├── test_local.py              # Local testing script
│   ├── setup_local.sh             # Local setup (Linux/Mac)
│   └── setup_local.bat            # Local setup (Windows)
│
├── deployment/                    # Deployment configs
│   ├── azure-managed-endpoint.yaml
│   └── n8n-workflow-example.json
│
├── docker-compose.yml             # Docker Compose for local testing
├── Dockerfile                     # Container definition
├── Makefile                       # Convenience commands
└── Documentation files...
```

## Quick Start

### 1. Local Testing with Swagger UI (No Azure)

```bash
# Windows
scripts\setup_local.bat

# Linux/Mac
bash scripts/setup_local.sh

# Process handbook
python scripts/process_handbook.py

# Run
python -m app.main

# Open Swagger UI in browser
# http://localhost:8000/docs

# Or test via command line
python scripts/test_local.py --query "What are the admission requirements?"
```

**Swagger UI Features:**
- Interactive API testing
- Request/response examples
- Schema validation
- Authentication support
- No need to write curl commands!

### 2. Azure Deployment

```bash
# Deploy all resources
python scripts/deploy_azure.py \
  --subscription <subscription-id> \
  --resource-group rag-student-support \
  --location eastus

# Configure .env with Azure credentials
# Run the service
python -m app.main
```

### 3. Cleanup

```bash
# Delete all Azure resources
python scripts/destroy_azure.py \
  --resource-group rag-student-support \
  --yes
```

## Key Features

### Local Mode (`MODE=local`)
- ✅ No Azure services required
- ✅ In-memory mock search service with sample knowledge base
- ✅ Mock OpenAI service (rule-based responses)
- ✅ Works completely offline
- ✅ Perfect for development and testing

### Azure Mode (`MODE=azure`)
- ✅ Real Azure AI Search integration
- ✅ Azure OpenAI with Semantic Kernel
- ✅ Production-ready deployment
- ✅ Full RAG capabilities

## Azure Resources Created

The deployment script creates (all cost-optimized):

| Resource | Tier | Cost |
|----------|------|------|
| Azure AI Search | Free | $0/month |
| Azure OpenAI | S0 (Standard) | Pay-per-use |
| Container Registry | Basic | ~$5/month |
| App Service Plan | F1 (Free) | $0/month |

**Total estimated cost**: ~$5-10/month for testing (mostly pay-per-use OpenAI)

## Commands Reference

### Using Makefile

```bash
make install          # Install dependencies
make local            # Run in local mode
make test             # Run tests
make docker-build     # Build Docker image
make docker-run       # Run with docker-compose
make deploy SUBSCRIPTION=<id> RESOURCE_GROUP=<name>  # Deploy to Azure
make destroy RESOURCE_GROUP=<name>                    # Destroy Azure resources
```

### Direct Scripts

```bash
# Local testing
python scripts/test_local.py --query "your question"

# Azure deployment
python scripts/deploy_azure.py --subscription <id> --resource-group <name>

# Cleanup
python scripts/destroy_azure.py --resource-group <name> --yes
```

## Environment Configuration

### Local Mode (.env)
```env
MODE=local
LOG_LEVEL=INFO
PORT=8000
```

### Azure Mode (.env)
```env
MODE=azure
AZURE_SEARCH_ENDPOINT=https://...
AZURE_SEARCH_KEY=...
AZURE_SEARCH_INDEX_NAME=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

## Testing Workflow

1. **Start Local**: Test with mock services
   ```bash
   MODE=local python -m app.main
   ```

2. **Test Locally**: Verify functionality
   ```bash
   python scripts/test_local.py --query "test question"
   ```

3. **Deploy to Azure**: Create resources
   ```bash
   python scripts/deploy_azure.py --subscription <id> --resource-group <name>
   ```

4. **Test Azure**: Switch to Azure mode
   ```bash
   MODE=azure python -m app.main
   ```

5. **Cleanup**: Delete resources when done
   ```bash
   python scripts/destroy_azure.py --resource-group <name> --yes
   ```

## Documentation

- **[RUN_SWAGGER_LOCALLY.md](RUN_SWAGGER_LOCALLY.md)** - Complete Swagger UI testing guide ⭐
- **[SWAGGER_QUICK_START.md](SWAGGER_QUICK_START.md)** - Quick Swagger UI reference
- **[README.md](README.md)** - Main documentation
- **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Local testing guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Azure deployment guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide

## Features

✅ **Local Testing**: No Azure required for development  
✅ **Automated Deployment**: One command to create all resources  
✅ **Cost Optimized**: Uses free/lowest tiers  
✅ **Resource Checking**: Safe to run multiple times  
✅ **Easy Cleanup**: One command to delete everything  
✅ **Docker Support**: Run with or without Docker  
✅ **Multilingual**: 12+ languages supported  
✅ **Guardrails**: Prevents hallucination  
✅ **Production Ready**: Error handling, logging, monitoring

## Next Steps

1. Test locally with mock services
2. Deploy to Azure when ready
3. Configure your knowledge base
4. Integrate with n8n
5. Deploy to production
