# Fixing "ModuleNotFoundError: No module named 'app'" When Debugging

## The Problem

When you try to debug `app/services/rag_service.py` directly, Python can't find the `app` module because the project root isn't in the Python path.

## Quick Fixes

### Solution 1: Use the Debug Script (Recommended)

I've created a debug script that fixes the path automatically:

```bash
conda activate rag-student-support
python scripts/debug_rag_service.py
```

This script:
- ✅ Adds project root to Python path
- ✅ Imports all necessary modules
- ✅ Sets up logging
- ✅ Tests the RAG service

### Solution 2: VS Code Launch Configuration

I've created `.vscode/launch.json` with proper configurations:

1. **Press F5** or go to Run → Start Debugging
2. Select **"Python: FastAPI Debug"** or **"Python: Debug RAG Service"**

The configuration automatically:
- ✅ Sets `PYTHONPATH` to project root
- ✅ Sets working directory correctly
- ✅ Enables debug logging

### Solution 3: Add Path in Code (For Direct File Debugging)

If you want to debug `rag_service.py` directly, add this at the top:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent  # Go up from app/services/
sys.path.insert(0, str(project_root))

# Now import app modules
from app.config import settings
```

### Solution 4: Set PYTHONPATH Environment Variable

**Windows PowerShell:**
```powershell
$env:PYTHONPATH = "C:\Users\brill\CursorProject\RAG"
python -m app.main
```

**Windows CMD:**
```cmd
set PYTHONPATH=C:\Users\brill\CursorProject\RAG
python -m app.main
```

**Linux/Mac:**
```bash
export PYTHONPATH=/path/to/RAG
python -m app.main
```

### Solution 5: Run as Module (Best for Production)

Always run the app as a module, not directly:

```bash
# ✅ Correct way
python -m app.main

# ❌ Wrong way (causes path issues)
python app/main.py
```

## VS Code Debugging Setup

### Option 1: Use Pre-configured Launch (Easiest)

1. Open VS Code
2. Press `F5` or go to Run → Start Debugging
3. Select **"Python: FastAPI Debug"**

### Option 2: Create Custom Launch Configuration

1. Create `.vscode/launch.json` (already created for you)
2. The configuration includes:
   - Proper `PYTHONPATH` setting
   - Working directory
   - Environment variables

### Option 3: Debug Specific File

1. Open the file you want to debug
2. Set breakpoints
3. Press `F5`
4. Select **"Python: Debug Current File"**

**Note:** For files with `from app.` imports, use the debug script instead.

## PyCharm Debugging Setup

1. **Create Run Configuration:**
   - Run → Edit Configurations
   - Click `+` → Python
   - Script path: `app/main.py`
   - Working directory: Project root
   - Environment variables: `PYTHONPATH=${PROJECT_DIR}`

2. **Or use Module:**
   - Run → Edit Configurations
   - Click `+` → Python
   - Module name: `app.main`
   - Working directory: Project root

## Testing the Fix

After applying a fix, test it:

```python
# This should work without errors
from app.config import settings
from app.services.rag_service import RAGService

print(f"Mode: {settings.mode}")
```

## Common Mistakes

### ❌ Don't Do This:
```python
# Running file directly
python app/services/rag_service.py  # ❌ Path issues
```

### ✅ Do This Instead:
```python
# Run as module
python -m app.main  # ✅ Works correctly

# Or use debug script
python scripts/debug_rag_service.py  # ✅ Works correctly
```

## Quick Reference

| Method | Command | When to Use |
|--------|--------|-------------|
| **Run as module** | `python -m app.main` | Normal operation |
| **Debug script** | `python scripts/debug_rag_service.py` | Debugging RAG service |
| **VS Code F5** | Press F5, select config | IDE debugging |
| **Set PYTHONPATH** | `$env:PYTHONPATH="..."` | Manual path setup |

## Still Having Issues?

1. **Check conda environment:**
   ```bash
   conda activate rag-student-support
   which python  # Should show conda python
   ```

2. **Verify project structure:**
   ```
   RAG/
   ├── app/
   │   ├── __init__.py
   │   ├── config.py
   │   └── services/
   │       └── rag_service.py
   └── scripts/
       └── debug_rag_service.py
   ```

3. **Check Python path:**
   ```python
   import sys
   print(sys.path)  # Should include project root
   ```

4. **Use the debug script:**
   ```bash
   python scripts/debug_rag_service.py
   ```
