# Azure Deployment Guide

## Prerequisites

1. Azure Container Registry (ACR)
2. Azure Kubernetes Service (AKS) or Azure Container Instances
3. Azure AI Search service configured
4. Azure OpenAI service configured

## Build and Push Docker Image

```bash
# Login to Azure
az login

# Login to ACR
az acr login --name your-registry-name

# Build image
docker build -t rag-student-support:latest .

# Tag for ACR
docker tag rag-student-support:latest your-registry.azurecr.io/rag-student-support:latest

# Push to ACR
docker push your-registry.azurecr.io/rag-student-support:latest
```

## Deploy to Azure Managed Endpoints

### Option 1: Azure Container Instances (Simpler)

```bash
az container create \
  --resource-group your-rg \
  --name rag-student-support \
  --image your-registry.azurecr.io/rag-student-support:latest \
  --registry-login-server your-registry.azurecr.io \
  --registry-username your-username \
  --registry-password your-password \
  --environment-variables \
    AZURE_SEARCH_ENDPOINT=your-endpoint \
    AZURE_SEARCH_KEY=your-key \
    AZURE_SEARCH_INDEX_NAME=your-index \
    AZURE_OPENAI_ENDPOINT=your-endpoint \
    AZURE_OPENAI_API_KEY=your-key \
  --dns-name-label rag-student-support \
  --ports 8000
```

### Option 2: Azure Kubernetes Service (Production)

1. Create Kubernetes secrets:
```bash
kubectl create secret generic rag-secrets \
  --from-literal=azure-search-endpoint=your-endpoint \
  --from-literal=azure-search-key=your-key \
  --from-literal=azure-search-index-name=your-index \
  --from-literal=azure-openai-endpoint=your-endpoint \
  --from-literal=azure-openai-api-key=your-key
```

2. Apply deployment:
```bash
kubectl apply -f azure-managed-endpoint.yaml
```

## Configure n8n Integration

In n8n, create an HTTP Request node pointing to your deployed endpoint:

- URL: `https://your-endpoint.azurecontainer.io/api/v1/query`
- Method: POST
- Headers: `X-API-Key: your-api-key`
- Body: JSON with `query`, `student_id` (optional), `language` (optional)

## Monitoring

- Health check: `GET /health`
- Logs: Use Azure Monitor or `kubectl logs` for AKS
- Metrics: Configure Application Insights for detailed monitoring
