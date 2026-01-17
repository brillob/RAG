# Azure Deployment Guide

Complete guide for deploying the RAG system to Azure with automated resource creation.

## Prerequisites

1. **Azure CLI installed**
   ```bash
   # Check installation
   az --version
   
   # If not installed, download from:
   # https://aka.ms/InstallAzureCLI
   ```

2. **Azure account with active subscription**
   ```bash
   # Login to Azure
   az login
   
   # List subscriptions
   az account list --output table
   
   # Set default subscription (optional)
   az account set --subscription <subscription-id>
   ```

## Automated Deployment

### Step 1: Deploy Azure Resources

Run the automated deployment script:

```bash
python scripts/deploy_azure.py \
  --subscription <your-subscription-id> \
  --resource-group rag-student-support \
  --location eastus
```

**What it creates:**
- ✅ Resource Group
- ✅ Azure AI Search (Free tier)
- ✅ Azure OpenAI service (S0 tier - lowest)
- ✅ Azure Container Registry (Basic tier - cheapest)
- ✅ App Service Plan (Free tier)

**Resource tiers used (cost-optimized):**
- Azure AI Search: **Free** (up to 50MB storage, 3 indexes)
- Azure OpenAI: **S0** (Standard tier - lowest available)
- Container Registry: **Basic** (cheapest tier)
- App Service Plan: **F1** (Free tier)

**Note:** The script checks if resources exist before creating them, so it's safe to run multiple times.

### Step 2: Configure Environment

After deployment, update your `.env` file with the created resources:

```bash
MODE=azure

# Get these from the deployment output
AZURE_SEARCH_ENDPOINT=https://<resource-group>-search.search.windows.net
AZURE_SEARCH_KEY=<from-deployment-output>
AZURE_SEARCH_INDEX_NAME=student-knowledge-base

AZURE_OPENAI_ENDPOINT=https://<resource-group>-openai.openai.azure.com
AZURE_OPENAI_API_KEY=<from-deployment-output>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Step 3: Create and Index Knowledge Base

1. **Create Search Index:**
   ```bash
   # Use Azure Portal or Azure CLI
   az search index create \
     --resource-group rag-student-support \
     --service-name <resource-group>-search \
     --name student-knowledge-base \
     --definition @index-definition.json
   ```

2. **Index your documents** (see Azure AI Search documentation)

### Step 4: Deploy Model to Azure OpenAI

1. Go to Azure Portal → Your OpenAI resource
2. Deploy a model (e.g., gpt-4 or gpt-35-turbo)
3. Note the deployment name

### Step 5: Build and Deploy Container

```bash
# Login to ACR
az acr login --name <registry-name>

# Build and push image
az acr build --registry <registry-name> \
  --image rag-student-support:latest .

# Or use Docker directly
docker build -t rag-student-support .
docker tag rag-student-support <registry-name>.azurecr.io/rag-student-support:latest
docker push <registry-name>.azurecr.io/rag-student-support:latest
```

### Step 6: Deploy to App Service

```bash
az webapp create \
  --resource-group rag-student-support \
  --plan <resource-group>-plan \
  --name rag-student-support-api \
  --deployment-container-image-name <registry-name>.azurecr.io/rag-student-support:latest

# Configure environment variables
az webapp config appsettings set \
  --resource-group rag-student-support \
  --name rag-student-support-api \
  --settings \
    MODE=azure \
    AZURE_SEARCH_ENDPOINT="..." \
    AZURE_SEARCH_KEY="..." \
    # ... other settings
```

## Manual Resource Creation

If you prefer to create resources manually:

### Azure AI Search

```bash
az search service create \
  --name <service-name> \
  --resource-group rag-student-support \
  --sku free \
  --location eastus
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name <service-name> \
  --resource-group rag-student-support \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

**Note:** Azure OpenAI requires approval and may not be available in all regions.

### Container Registry

```bash
az acr create \
  --name <registry-name> \
  --resource-group rag-student-support \
  --sku Basic \
  --admin-enabled true
```

## Destroying Resources

To delete all resources and stop incurring costs:

```bash
python scripts/destroy_azure.py \
  --resource-group rag-student-support \
  --subscription <subscription-id>
```

Or with auto-confirm:

```bash
python scripts/destroy_azure.py \
  --resource-group rag-student-support \
  --yes
```

**⚠️ WARNING:** This deletes ALL resources in the resource group permanently!

## Cost Optimization Tips

1. **Use Free Tiers:**
   - Azure AI Search Free (50MB, 3 indexes)
   - App Service Plan F1 (Free)

2. **Use Lowest Tiers:**
   - Container Registry Basic ($5/month)
   - Azure OpenAI S0 (pay-per-use)

3. **Delete When Not Testing:**
   ```bash
   # Destroy resources when done
   python scripts/destroy_azure.py --resource-group rag-student-support --yes
   ```

4. **Monitor Costs:**
   ```bash
   # Check resource costs
   az consumption usage list \
     --subscription <subscription-id> \
     --start-date $(date -d "1 month ago" +%Y-%m-%d) \
     --end-date $(date +%Y-%m-%d)
   ```

## Troubleshooting

### Resource Already Exists
The deployment script checks for existing resources and skips creation if they exist. This is safe.

### Azure OpenAI Not Available
Azure OpenAI requires approval. You may need to:
1. Request access in Azure Portal
2. Wait for approval
3. Create the service manually

### Deployment Fails
Check:
1. You're logged in: `az account show`
2. You have permissions: `az role assignment list --assignee <your-email>`
3. Region supports the services: Some services aren't available in all regions

### Container Build Fails
Ensure:
1. Docker is running
2. You're logged into ACR: `az acr login --name <registry-name>`
3. Image name follows ACR naming conventions

## Next Steps

After deployment:
1. Test the API endpoint
2. Configure n8n integration
3. Set up monitoring and alerts
4. Configure auto-scaling if needed
