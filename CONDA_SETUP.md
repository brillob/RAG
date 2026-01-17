# Anaconda/Conda Environment Setup Guide

This guide explains how to set up and use an Anaconda/Conda virtual environment for this project.

## Quick Start

### Option 1: Create Environment from YAML (Recommended)

```bash
# Create conda environment from environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate rag-student-support
```

### Option 2: Create Environment Manually

```bash
# Create a new conda environment with Python 3.11
conda create -n rag-student-support python=3.11

# Activate the environment
conda activate rag-student-support

# Install dependencies
pip install -r requirements.txt
```

## Using the Environment

### Activate Environment

**Windows (Anaconda Prompt or Command Prompt):**
```bash
conda activate rag-student-support
```

**Linux/Mac:**
```bash
conda activate rag-student-support
```

### Verify Environment is Active

You should see `(rag-student-support)` at the beginning of your command prompt:
```bash
(rag-student-support) C:\Users\brill\CursorProject\RAG>
```

### Install/Update Packages

Once the environment is activated, you can use pip normally:
```bash
# Install all dependencies
pip install -r requirements.txt

# Install a new package
pip install package-name

# Upgrade a package
pip install --upgrade package-name

# Install development dependencies
pip install -r requirements-dev.txt
```

### Run the Application

```bash
# Make sure environment is activated
conda activate rag-student-support

# Run the server
python -m app.main

# Or process the handbook
python scripts/process_handbook.py

# Or run tests
pytest
```

## Managing the Environment

### List All Environments
```bash
conda env list
```

### Deactivate Environment
```bash
conda deactivate
```

### Remove Environment
```bash
conda env remove -n rag-student-support
```

### Update Environment from YAML
```bash
# If environment.yml changes
conda env update -f environment.yml --prune
```

### Export Current Environment
```bash
# Export to YAML file
conda env export > environment.yml

# Export only pip packages (if you want to keep conda packages separate)
conda env export --from-history > environment.yml
```

## Common Issues

### Issue: "conda: command not found"

**Solution:**
- Make sure Anaconda/Miniconda is installed
- Add Anaconda to your PATH:
  - Windows: Add `C:\Users\YourName\anaconda3\Scripts` to PATH
  - Or use Anaconda Prompt instead of regular Command Prompt

### Issue: "Environment not activating"

**Solution:**
```bash
# Initialize conda for your shell (if needed)
conda init

# Then restart your terminal
```

### Issue: "Package conflicts"

**Solution:**
```bash
# Create a fresh environment
conda env remove -n rag-student-support
conda env create -f environment.yml
```

### Issue: "pip install fails"

**Solution:**
```bash
# Make sure you're in the activated environment
conda activate rag-student-support

# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

## IDE Integration

### VS Code / Cursor

1. Open the project folder
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Python: Select Interpreter"
4. Choose the conda environment: `rag-student-support`

Or create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${env:CONDA_PREFIX}/python.exe"
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click the gear icon → Add
3. Select "Conda Environment"
4. Choose "Existing environment"
5. Select: `C:\Users\YourName\anaconda3\envs\rag-student-support\python.exe`

## Workflow Example

```bash
# 1. Open Anaconda Prompt (Windows) or Terminal (Linux/Mac)

# 2. Navigate to project directory
cd C:\Users\brill\CursorProject\RAG

# 3. Activate environment
conda activate rag-student-support

# 4. Verify you're in the right environment
python --version  # Should show Python 3.11
which python      # Should show conda environment path

# 5. Install/update dependencies if needed
pip install -r requirements.txt

# 6. Run the application
python -m app.main

# 7. In another terminal, test it
python scripts/test_local.py --query "What are the admission requirements?"

# 8. When done, deactivate (optional)
conda deactivate
```

## Tips

1. **Always activate the environment** before running the app or installing packages
2. **Check your prompt** - you should see `(rag-student-support)` when active
3. **Use conda for Python version** - use pip for Python packages
4. **Keep environment.yml updated** - commit it to version control
5. **Use separate environments** - one per project to avoid conflicts

## Next Steps

After setting up the environment:

1. **Process the handbook:**
   ```bash
   python scripts/process_handbook.py
   ```

2. **Run the server:**
   ```bash
   python -m app.main
   ```

3. **Test with Swagger UI:**
   - Open http://localhost:8000/docs in your browser

4. **Run tests:**
   ```bash
   pytest
   ```

See [QUICKSTART.md](QUICKSTART.md) for more details.
