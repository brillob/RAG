# Quick Start - Swagger UI Testing

## 🚀 Quick Setup (3 Steps)

### 1. Process the Handbook
```bash
python scripts/process_handbook.py
```

### 2. Start the Server
```bash
python -m app.main
```

### 3. Open Swagger UI
Open your browser and go to:
**http://localhost:8000/docs**

That's it! You can now test the API interactively.

## 📝 Quick Test

1. In Swagger UI, find **POST /api/v1/query**
2. Click **"Try it out"**
3. Paste this example:
```json
{
  "query": "What are the enrolment requirements?"
}
```
4. Click **"Execute"**
5. See the response!

## 🔗 Available URLs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 💡 Pro Tips

- Use **"Authorize"** button if API key is required
- Copy `conversation_id` from response for follow-up questions
- Try different languages: `"language": "es"` for Spanish
- Check response `confidence` score (higher is better)

See [SWAGGER_GUIDE.md](SWAGGER_GUIDE.md) for detailed documentation.
