# How .env Files Work in This Application

## Current Configuration

The application is configured to look for **one specific file**: `.env` in the project root.

```python
class Config:
    env_file = ".env"  # Looks for this specific file
```

## What Happens with .env Files

### Single .env File

If you have **one `.env` file** in the project root:
- ✅ It will be loaded
- ✅ Values override defaults from `config.py`
- ✅ Missing values use defaults from `config.py`

### Multiple .env Files

**Current behavior:** The app only looks for `.env` (the exact filename specified in config).

If you have multiple `.env` files like:
- `.env`
- `.env.local`
- `.env.development`
- `.env.production`

**Only `.env` will be loaded** - the others are ignored.

### Priority Order (When Settings are Loaded)

Pydantic Settings loads configuration in this order (highest to lowest priority):

1. **Environment variables** (from your system/terminal)
   ```bash
   export LOCAL_LLM_MODEL=qwen2.5:0.5b
   ```

2. **`.env` file** (if it exists)
   ```env
   LOCAL_LLM_MODEL=tinyllama
   ```

3. **Default values in `config.py`**
   ```python
   local_llm_model: str = "tinyllama"  # Default
   ```

**Important:** Later sources **do not override** earlier ones. Once a value is set, it won't be changed by lower-priority sources.

## Examples

### Example 1: No .env File
```
Environment variables: (none)
.env file: (doesn't exist)
config.py defaults: LOCAL_LLM_MODEL=tinyllama

Result: Uses "tinyllama" ✅
```

### Example 2: .env File Exists
```
Environment variables: (none)
.env file: LOCAL_LLM_MODEL=qwen2.5:0.5b
config.py defaults: LOCAL_LLM_MODEL=tinyllama

Result: Uses "qwen2.5:0.5b" (from .env) ✅
```

### Example 3: Environment Variable Set
```
Environment variables: LOCAL_LLM_MODEL=phi3:mini
.env file: LOCAL_LLM_MODEL=qwen2.5:0.5b
config.py defaults: LOCAL_LLM_MODEL=tinyllama

Result: Uses "phi3:mini" (from environment, highest priority) ✅
```

### Example 4: Multiple .env Files
```
Files in project:
- .env (contains: LOCAL_LLM_MODEL=tinyllama)
- .env.local (contains: LOCAL_LLM_MODEL=qwen2.5:0.5b)
- .env.production (contains: LOCAL_LLM_MODEL=phi3:mini)

Result: Only .env is loaded, uses "tinyllama" ✅
Other files (.env.local, .env.production) are IGNORED
```

## How to Use Multiple .env Files

If you want to support multiple `.env` files (e.g., `.env.local`, `.env.production`), you would need to modify `config.py`:

### Option 1: Load Multiple Files Explicitly

```python
class Config:
    env_file = [".env.local", ".env"]  # Loads both, .env.local has priority
    case_sensitive = False
```

### Option 2: Environment-Specific Loading

```python
import os

class Config:
    # Load environment-specific .env file
    env_file = f".env.{os.getenv('ENVIRONMENT', 'local')}"  # .env.local, .env.production, etc.
    case_sensitive = False
```

### Option 3: Load with Override

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ... your settings ...
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
```

## Current Behavior Summary

| Scenario | What Happens |
|----------|--------------|
| No `.env` file | Uses defaults from `config.py` ✅ |
| One `.env` file | Loads it, overrides defaults ✅ |
| Multiple `.env` files | Only loads `.env`, ignores others ⚠️ |
| `.env` + environment variables | Environment variables win (higher priority) ✅ |
| `.env` file missing values | Uses defaults from `config.py` for missing values ✅ |

## Best Practices

1. **Use one `.env` file** for local development
2. **Keep `.env` in `.gitignore`** (already done)
3. **Use environment variables** for production/secrets
4. **Use `config.py` defaults** for sensible defaults

## Testing What's Loaded

You can check what configuration is actually being used:

```python
from app.config import settings

print(f"LLM Model: {settings.local_llm_model}")
print(f"Provider: {settings.local_llm_provider}")
print(f"Mode: {settings.mode}")
```

Or check the health endpoint: `http://localhost:8000/health`
