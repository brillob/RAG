# Quick Steps to Run Swagger UI Locally

## 🚀 5-Minute Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Process the Handbook
```bash
python scripts/process_handbook.py
```
**Wait for**: "✓ Processing complete!" message

### Step 3: Start the Server
```bash
python -m app.main
```
**Wait for**: "Uvicorn running on http://0.0.0.0:8000"

### Step 4: Open Swagger UI
**Open your browser and go to:**
```
http://localhost:8000/docs
```

### Step 5: Test the API
1. Click **POST /api/v1/query**
2. Click **"Try it out"** button
3. Paste this in the request body:
   ```json
   {
     "query": "What are the enrolment requirements?"
   }
   ```
4. Click **"Execute"**
5. View the response below!

## ✅ Success Indicators

- ✅ Server shows "Uvicorn running on http://0.0.0.0:8000"
- ✅ Browser loads Swagger UI at http://localhost:8000/docs
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ Query endpoint returns a response with enrolment information

## 🐛 Quick Troubleshooting

**Server won't start?**
- Check Python version: `python --version` (need 3.10+)
- Install dependencies: `pip install -r requirements.txt`
- Port in use? Change `PORT=8001` in `.env`

**Swagger UI not loading?**
- Check server is running (Step 3)
- Try `http://127.0.0.1:8000/docs`
- Check firewall settings

**No response or low confidence?**
- Run Step 2 again: `python scripts/process_handbook.py --reset`
- Check server logs for errors

## 📚 More Details

- **Complete Guide**: [RUN_SWAGGER_LOCALLY.md](RUN_SWAGGER_LOCALLY.md)
- **Quick Reference**: [SWAGGER_QUICK_START.md](SWAGGER_QUICK_START.md)
- **Testing Guide**: [SWAGGER_GUIDE.md](SWAGGER_GUIDE.md)

---

**That's it!** You're ready to test the API with Swagger UI! 🎉
