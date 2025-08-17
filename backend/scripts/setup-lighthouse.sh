#!/bin/bash

# Lighthouse CLI Setup Script for LeadGen Makeover Agent
# This script installs and configures Lighthouse CLI for the backend service

set -e

echo "🚀 Setting up Lighthouse CLI for LeadGen Makeover Agent Backend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node --version)"
    echo "   Please upgrade Node.js to version 18 or higher."
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm $(npm --version) detected"

# Install Lighthouse CLI globally
echo "📦 Installing Lighthouse CLI globally..."
npm install -g lighthouse@latest

# Verify installation
if ! command -v lighthouse &> /dev/null; then
    echo "❌ Lighthouse CLI installation failed"
    exit 1
fi

echo "✅ Lighthouse CLI $(lighthouse --version) installed successfully"

# Install Lighthouse CI
echo "📦 Installing Lighthouse CI..."
npm install -g @lhci/cli@latest

# Verify Lighthouse CI installation
if ! command -v lhci &> /dev/null; then
    echo "❌ Lighthouse CI installation failed"
    exit 1
fi

echo "✅ Lighthouse CI installed successfully"

# Install project dependencies
echo "📦 Installing project dependencies..."
npm install

# Test Lighthouse CLI
echo "🧪 Testing Lighthouse CLI..."
lighthouse --version

# Test Lighthouse CI
echo "🧪 Testing Lighthouse CI..."
lhci --version

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update .env file with your actual API keys and configuration"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Lighthouse CLI setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Test with: npm run lighthouse:test"
echo "3. Run audit with: npm run lighthouse:audit"
echo "4. Run CI with: npm run lighthouse:ci"
echo ""
echo "For more information, visit:"
echo "  - https://developer.chrome.com/docs/lighthouse/overview"
echo "  - https://github.com/GoogleChrome/lighthouse-ci"
