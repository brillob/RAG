# Quick Start Guide

## Choose Your Path

- **Local Testing (No Azure)**: Test the system with vector database and Swagger UI
- **Azure Deployment**: Deploy to Azure with automated resource creation

## Local Testing with Swagger UI (Recommended First)

### Quick Start - 5 Minutes

1. **Setup:**
   ```bash
   # Windows
   scripts\setup_local.bat
   
   # Linux/Mac
   bash scripts/setup_local.sh
   ```

2. **Process the Handbook:**
   ```bash
   python scripts/process_handbook.py
   ```

3. **Start the Server:**
   ```bash
   python -m app.main
   ```

4. **Open Swagger UI:**
   - Open browser: **http://localhost:8000/docs**
   - Click **POST /api/v1/query**
   - Click **"Try it out"**
   - Paste example request:
     ```json
     {
       "query": "What are the enrolment requirements?"
     }
     ```
   - Click **"Execute"**
   - View the response!

5. **Alternative Testing:**
   ```bash
   python scripts/test_local.py --query "What are the admission requirements?"
   ```

That's it! The system runs with real vector database and Swagger UI - no Azure needed.

See [SWAGGER_GUIDE.md](SWAGGER_GUIDE.md) for detailed Swagger UI testing guide.
See [LOCAL_TESTING.md](LOCAL_TESTING.md) for more details.

## Azure Deployment

### Prerequisites Setup

### Automated Deployment (Recommended)

Deploy all Azure resources automatically:

```bash
python scripts/deploy_azure.py \
  --subscription <your-subscription-id> \
  --resource-group rag-student-support \
  --location eastus
```

This creates:
- ✅ Resource Group
- ✅ Azure AI Search (Free tier)
- ✅ Azure OpenAI (S0 tier)
- ✅ Container Registry (Basic tier)
- ✅ App Service Plan (Free tier)

**Cost-optimized**: Uses free/lowest tiers to minimize costs.

### Manual Setup (Alternative)

#### 1. Azure AI Search Setup

1. Create an Azure AI Search service in Azure Portal
2. Create an index with the following fields:
   - `content` (Searchable, Analyzer: standard.lucene)
   - `title` (Searchable)
   - `source` (Filterable)
   - Configure semantic search with a semantic configuration named "default"

3. Index your knowledge base documents

### 2. Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy a model (e.g., gpt-4 or gpt-35-turbo)
3. Note the deployment name, endpoint, and API key

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your Azure credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values.

## Cleanup

When done testing, destroy all Azure resources:

```bash
python scripts/destroy_azure.py \
  --resource-group rag-student-support \
  --yes
```

⚠️ **WARNING**: This permanently deletes all resources!

## Docker Deployment

### Build Image

```bash
docker build -t rag-student-support .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env rag-student-support
```

## n8n Integration

1. In n8n, create a new workflow
2. Add an HTTP Request node
3. Configure:
   - Method: POST
   - URL: `http://your-api-endpoint/api/v1/query`
   - Headers: `X-API-Key: your-api-key`
   - Body: JSON
     ```json
     {
       "query": "{{ $json.query }}",
       "language": "auto"
     }
     ```
4. Connect to your WhatsApp trigger node

## Troubleshooting

### Common Issues

1. **Azure Search Connection Error**
   - Verify endpoint URL and API key
   - Check index name matches configuration
   - Ensure semantic search is configured

2. **Semantic Kernel Errors**
   - The code includes fallback to direct OpenAI API
   - Check Azure OpenAI deployment name and endpoint

3. **Language Detection Issues**
   - Ensure `langdetect` package is installed
   - For short queries, language detection may be less accurate

4. **Low Confidence Scores**
   - Adjust `min_confidence_score` in settings
   - Review search results quality
   - Check if knowledge base is properly indexed

## Next Steps

- Configure monitoring and logging
- Set up Azure Managed Endpoints deployment
- Integrate with WhatsApp via n8n
- Fine-tune prompt templates for your use case
- Add more languages to supported list
