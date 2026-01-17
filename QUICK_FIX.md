# Quick Fix: Module Import Errors

## Problem
When running scripts, you get errors like:
- `ModuleNotFoundError: No module named 'app'`
- `ModuleNotFoundError: No module named 'chromadb'`

## Solutions

### Solution 1: Activate Conda Environment (Most Common)

Make sure you're in your conda environment:

```bash
# Activate your environment
conda activate rag-student-support

# Or if you named it differently
conda activate c

# Verify you're in the right environment
python --version
python -c "import chromadb; print('OK')"
```

### Solution 2: Run from Project Root

Always run scripts from the project root directory:

```bash
# Make sure you're in the project root
cd C:\Users\brill\CursorProject\RAG

# Then run the script
python scripts/process_handbook.py
```

### Solution 3: Use the Batch Script (Windows)

On Windows, use the provided batch script:

```bash
scripts\run_process_handbook.bat
```

### Solution 4: Install Missing Packages

If packages are missing, install them:

```bash
# Make sure environment is activated
conda activate rag-student-support

# Install all dependencies
pip install -r requirements.txt
```

### Solution 5: Verify Installation

Check if packages are installed:

```bash
python -c "import chromadb; print('chromadb:', chromadb.__version__)"
python -c "import sentence_transformers; print('sentence-transformers OK')"
python scripts/verify_dependencies.py
```

## Common Issues

### Issue: "No module named 'app'"
**Fixed!** The script now adds the project root to Python path automatically.

### Issue: "No module named 'chromadb'"
**Solution:** 
1. Activate your conda environment: `conda activate rag-student-support`
2. Install: `pip install chromadb==0.4.22`
3. Or reinstall all: `pip install -r requirements.txt`

### Issue: Wrong Python Version
**Solution:**
```bash
# Check which Python is being used
where python
python --version

# Should show Python 3.11 from your conda environment
```

### Issue: Packages Installed in Wrong Environment
**Solution:**
```bash
# Make sure you're in the right environment
conda activate rag-student-support

# Verify
python -c "import sys; print(sys.executable)"
# Should show path to your conda environment's Python
```

## Recommended Workflow

1. **Open Anaconda Prompt** (not regular PowerShell/CMD)
2. **Navigate to project:**
   ```bash
   cd C:\Users\brill\CursorProject\RAG
   ```
3. **Activate environment:**
   ```bash
   conda activate rag-student-support
   ```
4. **Verify setup:**
   ```bash
   python scripts/verify_dependencies.py
   ```
5. **Run scripts:**
   ```bash
   python scripts/process_handbook.py
   ```

## Still Having Issues?

1. Check your conda environment is active (you should see `(rag-student-support)` in prompt)
2. Verify Python path: `python -c "import sys; print(sys.executable)"`
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Run verification: `python scripts/verify_dependencies.py`
