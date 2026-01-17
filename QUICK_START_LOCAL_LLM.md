# Quick Start: Very Small Local LLM for RAG

This guide shows you how to set up the **smallest possible** language model for RAG tasks on your laptop.

## Recommended: TinyLlama (1.1B parameters, ~637MB)

This is the **smallest practical model** that works well for RAG/QA tasks.

### Quick Setup (Ollama)

1. **Install Ollama** (if not already installed):
   - Windows: Download from https://ollama.com/download
   - Mac/Linux: `curl -fsSL https://ollama.com/install.sh | sh`

2. **Pull the tiny model**:
   ```bash
   ollama pull tinyllama
   ```
   This downloads ~637MB - very small!

3. **Start your RAG server**:
   ```bash
   conda activate rag-student-support
   python -m app.main
   ```

That's it! The system will automatically use `tinyllama`.

### Even Smaller Option: Qwen2.5-0.5B (~376MB)

If you want an even smaller model:

```bash
ollama pull qwen2.5:0.5b
```

Then update `.env`:
```env
LOCAL_LLM_MODEL=qwen2.5:0.5b
```

## Alternative: Transformers with FLAN-T5-Small (80M params)

For the **smallest possible** model using transformers:

1. **Install transformers** (optional):
   ```bash
   conda activate rag-student-support
   pip install transformers accelerate
   ```

2. **Update `.env`**:
   ```env
   LOCAL_LLM_PROVIDER=transformers
   LOCAL_LLM_MODEL=google/flan-t5-small
   ```

3. **Start the server**:
   ```bash
   python -m app.main
   ```

The first run will download the model (~300MB). `flan-t5-small` is specifically designed for instruction following and RAG tasks!

## Model Comparison

| Model | Size | RAM Usage | Best For |
|-------|------|-----------|----------|
| **tinyllama** (Ollama) | 1.1B params | ~1.5GB | General RAG tasks |
| **qwen2.5:0.5b** (Ollama) | 500M params | ~1GB | Ultra-lightweight |
| **flan-t5-small** (Transformers) | 80M params | ~500MB | RAG/QA tasks (best quality) |

## Testing

Once running, test at: http://localhost:8000/docs

Try: "What are the enrolment requirements?"

## Troubleshooting

**Out of memory?** Use `qwen2.5:0.5b` or `flan-t5-small` instead.

**Too slow?** Make sure you're using Ollama (faster than transformers).

**Model not found?** Run: `ollama pull tinyllama`
