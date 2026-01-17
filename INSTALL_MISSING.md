# Installing Missing Dependencies

If you encounter `ModuleNotFoundError` for packages that should be installed, follow these steps:

## Quick Fix

1. **Activate your conda environment:**
   ```bash
   conda activate rag-student-support
   ```

2. **Verify you're in the right environment:**
   ```bash
   python -c "import sys; print(sys.executable)"
   # Should show: ...\rag-student-support\python.exe
   ```

3. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Common Missing Packages

### sentence-transformers
```bash
pip install sentence-transformers==2.2.2
```

### chromadb
```bash
pip install chromadb==0.4.22
```

### Other packages
```bash
# Install all at once
pip install -r requirements.txt
```

## Verify Installation

After installing, verify packages are available:

```bash
python scripts/verify_dependencies.py
```

Or test individual imports:
```bash
python -c "import chromadb; print('chromadb OK')"
python -c "import sentence_transformers; print('sentence-transformers OK')"
```

## Troubleshooting

### Issue: Packages install to user site-packages instead of conda environment

**Symptoms:** 
- See "Defaulting to user installation because normal site-packages is not writeable"
- Packages installed but still get import errors

**Solution:**
1. Make sure conda environment is activated (you should see `(rag-student-support)` in prompt)
2. Use `python -m pip install` instead of just `pip install`
3. Check Python path: `python -c "import sys; print(sys.executable)"`

### Issue: Still can't import after installation

**Solution:**
1. Verify you're using the right Python:
   ```bash
   which python  # Linux/Mac
   where python  # Windows
   ```
2. Reinstall in the conda environment:
   ```bash
   conda activate rag-student-support
   python -m pip install --force-reinstall sentence-transformers==2.2.2
   ```

### Issue: Permission errors

**Solution:**
- Don't use `sudo` or run as administrator
- Make sure conda environment is activated
- Use `python -m pip install` instead of `pip install`

## Complete Reinstall

If nothing works, reinstall all dependencies:

```bash
# Activate environment
conda activate rag-student-support

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install all requirements
python -m pip install -r requirements.txt

# Verify
python scripts/verify_dependencies.py
```
