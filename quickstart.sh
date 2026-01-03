#!/bin/bash

# AI-OpenSCAD Quick Start Script
# This script automates the initial setup

set -e

echo "========================================="
echo "   AI-OpenSCAD Quick Start"
echo "========================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker found"
echo "✓ Docker Compose found"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    echo ""
    echo "⚠️  IMPORTANT: You need to add your OpenAI API key!"
    echo ""
    echo "1. Get an API key from: https://platform.openai.com/api-keys"
    echo "2. Edit the .env file and replace 'sk-your-openai-api-key-here'"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
    
    # Check if user actually added the key
    if grep -q "sk-your-openai-api-key-here" .env; then
        echo ""
        echo "⚠️  It looks like you haven't updated the API key yet."
        echo "Please edit .env and add your OpenAI API key, then run this script again."
        exit 1
    fi
else
    echo "✓ .env file found"
fi

echo ""
echo "🚀 Starting AI-OpenSCAD..."
echo "This may take a few minutes on first run (downloading images)..."
echo ""

# Build and start services
docker compose up -d --build

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "========================================="
    echo "✅ AI-OpenSCAD is running!"
    echo "========================================="
    echo ""
    echo "🌐 Open in your browser:"
    echo "   http://localhost:4100"
    echo ""
    echo "📊 View logs:"
    echo "   docker compose logs -f"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker compose down"
    echo ""
    echo "Try generating: 'M8 bolt with threads, 30mm long'"
    echo ""
else
    echo ""
    echo "❌ Something went wrong. Check logs with:"
    echo "   docker compose logs"
    exit 1
fi
