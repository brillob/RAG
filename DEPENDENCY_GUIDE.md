# Dependency Management Guide

This guide ensures all dependencies are correctly installed and compatible.

## Quick Setup

### Using Conda (Recommended)

1. **Create/activate environment:**
   ```bash
   conda env create -f environment.yml
   conda activate rag-student-support
   ```

2. **Or update existing:**
   ```bash
   conda env update -f environment.yml --prune
   ```

### Using pip

1. **Install dependencies:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

2. **For development:**
   ```bash
   pip install -r requirements-dev.txt
   ```

## Verify Installation

Run the verification script:
```bash
python scripts/verify_dependencies.py
```

This checks:
- Python version compatibility (3.10+)
- All required packages are installed
- No dependency conflicts

## Key Dependencies

### Core Framework
- **fastapi==0.104.1** - Web framework
- **uvicorn[standard]==0.24.0** - ASGI server
- **pydantic==2.5.0** - Data validation

### Azure Services (for Azure mode)
- **semantic-kernel>=1.30.0,<2.0.0** - AI orchestration
- **azure-search-documents==11.4.0** - Azure AI Search
- **azure-identity==1.15.0** - Azure authentication

### Local RAG (for local mode)
- **chromadb==0.4.22** - Vector database
- **sentence-transformers==2.2.2** - Embeddings
- **numpy>=1.24.0,<2.0.0** - Numerical operations
- **torch>=2.0.0,<3.0.0** - ML framework (for sentence-transformers)

### PDF Processing
- **pypdf==3.17.4** - PDF text extraction
- **pdfplumber==0.10.3** - Advanced PDF parsing

### Utilities
- **langdetect==1.0.9** - Language detection
- **openai==1.3.0** - OpenAI SDK
- **python-dotenv==1.0.0** - Environment variables

## Version Compatibility Notes

### Python Version
- **Required:** Python 3.10 or higher
- **Recommended:** Python 3.11 (as specified in environment.yml)
- **Tested with:** Python 3.11, 3.12

### numpy and torch
- Versions are flexible (`>=1.24.0,<2.0.0` for numpy, `>=2.0.0,<3.0.0` for torch)
- These ranges ensure compatibility with:
  - sentence-transformers 2.2.2
  - chromadb 0.4.22
  - Python 3.11+

### semantic-kernel
- **Fixed:** Changed from non-existent `0.9.0` to `>=1.30.0,<2.0.0`
- Available versions start at 1.30.0
- Latest stable: 1.39.0 (as of Nov 2025)

## Troubleshooting

### Issue: "No matching distribution found for semantic-kernel==0.9.0"
**Solution:** Already fixed in requirements.txt. Use `>=1.30.0,<2.0.0`

### Issue: numpy/torch compatibility errors
**Solution:** Versions are now flexible. If issues persist:
```bash
pip install --upgrade pip
pip install numpy>=1.24.0 torch>=2.0.0
```

### Issue: chromadb installation fails
**Solution:** chromadb requires specific build tools on Windows:
```bash
# Install build tools first
pip install --upgrade pip setuptools wheel
pip install chromadb==0.4.22
```

### Issue: Dependency conflicts
**Solution:** Run pip check:
```bash
pip check
```
If conflicts are found, update the conflicting packages or use a fresh environment.

### Issue: Import errors after installation
**Solution:** Verify installation:
```bash
python scripts/verify_dependencies.py
```

## Best Practices

1. **Always use a virtual environment** (conda or venv)
2. **Pin versions for production** (use `==` in requirements.txt)
3. **Use flexible ranges for transitive deps** (e.g., numpy, torch)
4. **Test after updates** - Run verification script
5. **Keep requirements.txt updated** - Add new packages as needed

## Updating Dependencies

### Add a new package:
1. Add to `requirements.txt`
2. Install: `pip install package-name`
3. Test: `python scripts/verify_dependencies.py`
4. Commit changes

### Update existing package:
1. Update version in `requirements.txt`
2. Install: `pip install --upgrade package-name`
3. Test thoroughly
4. Update `environment.yml` if using conda

### Freeze current versions:
```bash
pip freeze > requirements-lock.txt
```
Use this for exact reproducibility in production.

## Development Dependencies

Install development tools:
```bash
pip install -r requirements-dev.txt
```

Includes:
- pytest - Testing framework
- black - Code formatting
- flake8 - Linting
- mypy - Type checking
- coverage - Test coverage

## Production Deployment

For production:
1. Use exact versions (already pinned in requirements.txt)
2. Test in staging first
3. Consider using `requirements-lock.txt` for exact reproducibility
4. Run `pip check` before deployment

## Support

If you encounter dependency issues:
1. Check Python version: `python --version`
2. Run verification: `python scripts/verify_dependencies.py`
3. Check for conflicts: `pip check`
4. Review error messages for specific package issues
