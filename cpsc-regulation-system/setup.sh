#!/bin/bash

# CPSC Regulation System Setup Script

echo "🚀 Setting up CPSC Regulation System..."
echo "====================================="

# Check system requirements
echo "🔍 Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ and try again."
    exit 1
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python $PYTHON_VERSION found"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Please install Node.js 16+ and try again."
    exit 1
else
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION found"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    echo "   Please install npm and try again."
    exit 1
else
    NPM_VERSION=$(npm --version)
    echo "✅ npm $NPM_VERSION found"
fi

echo ""
echo "📦 Setting up Backend..."

# Setup backend
cd backend

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup completed!"

echo ""
echo "🎨 Setting up Frontend..."

# Setup frontend
cd ../frontend

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup completed!"

echo ""
echo "🎉 Setup completed successfully!"
echo "====================================="
echo ""
echo "To start the system:"
echo "   ./start.sh"
echo ""
echo "To test the system:"
echo "   python test_system.py"
echo ""
echo "Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"