#!/bin/bash
# Setup script for local testing

echo "🚀 Setting up RAG Student Support for local testing..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.local.example .env
    echo "✓ Created .env file. You can edit it if needed."
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the server:"
echo "  source venv/bin/activate"
echo "  python -m app.main"
echo ""
echo "To test:"
echo "  python scripts/test_local.py --query 'What are the admission requirements?'"
echo ""
