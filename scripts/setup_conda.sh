#!/bin/bash
# Setup script for Anaconda/Conda environment (Linux/Mac)

echo "🚀 Setting up RAG Student Support with Conda..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "   Please install Anaconda or Miniconda"
    echo "   Or add conda to your PATH"
    exit 1
fi

echo "✓ Conda found"

# Check if environment.yml exists
if [ ! -f "environment.yml" ]; then
    echo "❌ environment.yml not found"
    echo "   Creating from requirements.txt..."
    echo "   Please run this script again after environment.yml is created"
    exit 1
fi

# Check if environment already exists
if conda env list | grep -q "rag-student-support"; then
    echo "⚠ Conda environment 'rag-student-support' already exists"
    echo "   Updating environment..."
    conda env update -f environment.yml --prune
else
    echo "📦 Creating conda environment from environment.yml..."
    conda env create -f environment.yml
fi

if [ $? -ne 0 ]; then
    echo "❌ Failed to create/update conda environment"
    exit 1
fi

echo ""
echo "✅ Conda environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  conda activate rag-student-support"
echo ""
echo "Then you can:"
echo "  - Run the server: python -m app.main"
echo "  - Process handbook: python scripts/process_handbook.py"
echo "  - Run tests: pytest"
echo ""
echo "To deactivate: conda deactivate"
echo ""
