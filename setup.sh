#!/bin/bash
# Simple setup script for development environment

set -e  # Exit on any error

echo "🚀 AI Avatar Platform - Environment Setup"
echo "========================================="

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Found Python: $python_version"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo "❌ Python 3.9+ required (MetaGPT supports 3.9-3.12). Please upgrade Python."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -e ".[dev]"
else
    python3 -m pip install -e ".[dev]"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

# Copy config template if needed
if [ ! -f "config/config2.yaml" ]; then
    echo "📋 Setting up configuration..."
    cp config/config2.example.yaml config/config2.yaml
    echo "⚠️  Please update API keys in config/config2.yaml"
fi

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "import metagpt; print(f'✅ MetaGPT: {metagpt.__version__}')" || echo "⚠️  MetaGPT not available"
python3 -c "import aiohttp; print(f'✅ aiohttp: {aiohttp.__version__}')"
python3 -c "import yaml; print(f'✅ PyYAML: {yaml.__version__}')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick start:"
echo "   python3 test_infrastructure.py    # Test infrastructure"
echo "   python3 -m pytest                 # Run all tests"
echo "   python3 main.py --help            # See platform options"
echo ""
echo "📖 See DEV_WORKFLOW.md for detailed instructions"