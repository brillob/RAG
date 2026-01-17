# Local LLM Setup Guide

This guide explains how to set up and use a local language model instead of the mock OpenAI service for local development and testing.

## Overview

The RAG system now supports running lightweight language models locally on your laptop. This provides real AI-generated responses based on your knowledge base, without requiring API keys or internet connectivity.

## Supported Providers

### 1. Ollama (Recommended) ⭐

**Ollama** is the easiest and most efficient option. It runs models locally with minimal setup.

**Advantages:**
- Very easy to install and use
- Optimized for local inference
- Supports many lightweight models
- Low memory footprint
- Fast inference on CPU

**Recommended Small Models for RAG:**
- `tinyllama` - **Smallest option** (1.1B params, ~637MB) - Perfect for laptops (default)
- `qwen2.5:0.5b` - **Even smaller** (500M params, ~376MB) - Ultra-lightweight
- `llama3.2:1b` - Lightweight and fast (1B params)
- `phi3:mini` - Microsoft's small but capable model (3.8B params)

### 2. Transformers (Alternative)

Uses HuggingFace's `transformers` library to run models directly.

**Advantages:**
- No separate service needed
- Direct model access
- More control over inference

**Disadvantages:**
- Slower than Ollama
- Higher memory usage
- First-time model download can be large

**Recommended Small Models for RAG:**
- `google/flan-t5-small` - **Best for RAG** (80M params) - Specifically designed for instruction following/QA
- `Qwen/Qwen2.5-0.5B-Instruct` - Very lightweight (500M params)
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` - Small chat model (1.1B params)

## Setup Instructions

### Option A: Using Ollama (Recommended)

#### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.com/download
2. Run the installer
3. Ollama will start automatically

**Mac/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Step 2: Pull a Model

Open a terminal and run:
```bash
# For the default very small model (recommended for RAG)
ollama pull tinyllama

# Or try even smaller:
ollama pull qwen2.5:0.5b

# Or slightly larger but faster:
ollama pull llama3.2:1b
```

#### Step 3: Verify Ollama is Running

```bash
# Check if Ollama is running
ollama list

# Test the model
ollama run llama3.2:1b "Hello, how are you?"
```

#### Step 4: Configure the Application

The default configuration already uses Ollama. You can customize it in `.env`:

```env
LOCAL_LLM_PROVIDER=ollama
LOCAL_LLM_MODEL=tinyllama
LOCAL_LLM_BASE_URL=http://localhost:11434
```

#### Step 5: Start the Application

```bash
conda activate rag-student-support
python -m app.main
```

The application will automatically connect to Ollama and use the local model!

### Option B: Using Transformers

#### Step 1: Install Transformers (Optional)

If you want to use transformers instead of Ollama:

```bash
conda activate rag-student-support
pip install transformers accelerate
```

**Note:** `torch` is already installed, but you may need to install `accelerate` for better performance.

#### Step 2: Configure the Application

Update `.env`:

```env
LOCAL_LLM_PROVIDER=transformers
LOCAL_LLM_MODEL=google/flan-t5-small
LOCAL_LLM_USE_GPU=false
```

**Note:** `flan-t5-small` is specifically designed for instruction following and RAG tasks, making it perfect for QA applications.

#### Step 3: Start the Application

The first run will download the model (this may take a few minutes):

```bash
conda activate rag-student-support
python -m app.main
```

## Configuration Options

Add these to your `.env` file or set as environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOCAL_LLM_PROVIDER` | `ollama` | Provider: `ollama` or `transformers` |
| `LOCAL_LLM_MODEL` | `llama3.2:1b` | Model name/ID |
| `LOCAL_LLM_BASE_URL` | `http://localhost:11434` | Ollama API URL (Ollama only) |
| `LOCAL_LLM_USE_GPU` | `false` | Use GPU for transformers (if available) |

## Model Recommendations

### For Laptops (8GB RAM) - Smallest Options

- **Ollama:** `tinyllama` (1.1B, ~637MB), `qwen2.5:0.5b` (500M, ~376MB) - **smallest**
- **Transformers:** `google/flan-t5-small` (80M params) - **best for RAG/QA tasks**

### For Better Performance (16GB+ RAM)

- **Ollama:** `llama3.2:3b`, `phi3:medium`, `gemma2:2b`
- **Transformers:** `microsoft/Phi-3-mini-128k-instruct`

## Troubleshooting

### Ollama Connection Error

**Error:** `Cannot connect to Ollama at http://localhost:11434`

**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Check if the port is correct (default: 11434)
3. Verify the model is pulled: `ollama list`

### Model Not Found (Ollama)

**Error:** `Model 'llama3.2:1b' not found`

**Solution:**
```bash
ollama pull llama3.2:1b
```

### Out of Memory (Transformers)

**Error:** `CUDA out of memory` or system runs out of RAM

**Solution:**
1. Use a smaller model (e.g., `qwen2.5:0.5b`)
2. Set `LOCAL_LLM_USE_GPU=false` to use CPU
3. Close other applications to free memory

### Slow Performance

**Solutions:**
1. Use Ollama instead of transformers (much faster)
2. Use a smaller model
3. Enable GPU if available: `LOCAL_LLM_USE_GPU=true`
4. Reduce `max_response_length` in config

### Fallback to Mock OpenAI

If the local LLM fails to initialize, the system automatically falls back to the mock OpenAI service. Check the logs for the error message.

## Testing

### Test Ollama Directly

```bash
ollama run llama3.2:1b "What are the admission requirements?"
```

### Test via API

Once the server is running, test via Swagger UI:
1. Open: http://localhost:8000/docs
2. Use the `/api/v1/query` endpoint
3. Ask: "What are the enrolment requirements?"

### Check Health

The application logs will show:
```
Local LLM service initialized: ollama (llama3.2:1b)
```

## Performance Comparison

| Provider | Model | Size | RAM Usage | Speed | Quality (RAG) |
|----------|-------|------|-----------|-------|---------------|
| Ollama | tinyllama | 1.1B | ~1.5GB | Very Fast | Good |
| Ollama | qwen2.5:0.5b | 500M | ~1GB | Very Fast | Good |
| Ollama | llama3.2:1b | 1B | ~2GB | Fast | Good |
| Transformers | flan-t5-small | 80M | ~500MB | Fast | Excellent (RAG) |

## Next Steps

1. **Start with Ollama** - It's the easiest and fastest option
2. **Try different models** - Find the balance between speed and quality
3. **Monitor performance** - Check response times and memory usage
4. **Customize prompts** - Adjust system prompts in `rag_service.py` if needed

## Additional Resources

- **Ollama Documentation:** https://ollama.com/docs
- **HuggingFace Models:** https://huggingface.co/models
- **Model Comparison:** https://ollama.com/library
