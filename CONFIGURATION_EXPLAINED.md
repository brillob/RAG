# Configuration Explained: .env vs config.py

## Quick Answer

**You don't need a `.env` file!** The application works perfectly with defaults from `config.py`.

## How Configuration Works

The application uses **Pydantic Settings** which loads configuration in this order (highest to lowest priority):

1. **Environment variables** (from your system/terminal) ← Highest priority
2. **`.env` file** (if it exists in project root) ← Optional!
3. **Default values in `config.py`** ← Lowest priority (always used as fallback)

**Important:** Once a value is set by a higher-priority source, it won't be overridden by lower-priority sources.

### Example

In `config.py`:
```python
local_llm_model: str = "tinyllama"  # Default value
```

This means:
- ✅ **Without `.env`**: Uses `"tinyllama"` (default)
- ✅ **With `.env` containing `LOCAL_LLM_MODEL=qwen2.5:0.5b`**: Uses `"qwen2.5:0.5b"` (overrides default)

## Why `.env` is Optional

The `.env` file is:
- **Optional** - Only needed if you want to override defaults
- **Gitignored** - Not committed to repository (for security)
- **Convenient** - Easy way to set environment variables locally

## When to Use `.env`

Use `.env` when you want to:
- Override default settings without changing code
- Keep secrets out of code (API keys, etc.)
- Have different configs for different environments

## Current Setup

Since you don't have a `.env` file, the app uses all defaults from `config.py`:
- `MODE=local` (default)
- `LOCAL_LLM_MODEL=tinyllama` (default)
- `LOCAL_LLM_PROVIDER=ollama` (default)
- etc.

**This is perfectly fine!** The app works great with defaults.

## Creating a `.env` File (Optional)

If you want to customize settings, create a `.env` file in the project root:

```env
# Override any default from config.py
LOCAL_LLM_MODEL=qwen2.5:0.5b
LOG_LEVEL=DEBUG
```

See `.env.example` for all available options.

## Multiple .env Files

**Current behavior:** The app only looks for `.env` (the exact filename specified in config).

If you have multiple `.env` files (like `.env.local`, `.env.production`), **only `.env` will be loaded** - the others are ignored.

See `ENV_FILES_EXPLAINED.md` for detailed explanation of how multiple .env files work.

## Summary

| Question | Answer |
|----------|--------|
| Do I need `.env`? | **No** - defaults in `config.py` work fine |
| Why does README mention `.env`? | It's an optional way to customize settings |
| Where are defaults? | In `app/config.py` |
| Can I use the app without `.env`? | **Yes!** It works out of the box |
