# Lighthouse CLI Setup Script for LeadGen Makeover Agent Backend (Windows)
# This script installs and configures Lighthouse CLI for the backend service

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Lighthouse CLI for LeadGen Makeover Agent Backend..." -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Host "✅ Node.js $nodeVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18+ first." -ForegroundColor Red
    Write-Host "   Visit: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js version
$nodeMajorVersion = [int]($nodeVersion -replace 'v(\d+)\.\d+\.\d+', '$1')
if ($nodeMajorVersion -lt 18) {
    Write-Host "❌ Node.js version 18+ is required. Current version: $nodeVersion" -ForegroundColor Red
    Write-Host "   Please upgrade Node.js to version 18 or higher." -ForegroundColor Yellow
    exit 1
}

# Check if npm is available
try {
    $npmVersion = npm --version
    if ($LASTEXITCODE -ne 0) {
        throw "npm not found"
    }
    Write-Host "✅ npm $npmVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ npm is not installed. Please install npm first." -ForegroundColor Red
    exit 1
}

# Install Lighthouse CLI globally
Write-Host "📦 Installing Lighthouse CLI globally..." -ForegroundColor Blue
npm install -g lighthouse@latest

# Verify installation
try {
    $lighthouseVersion = lighthouse --version
    if ($LASTEXITCODE -ne 0) {
        throw "Lighthouse CLI installation failed"
    }
    Write-Host "✅ Lighthouse CLI $lighthouseVersion installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Lighthouse CLI installation failed" -ForegroundColor Red
    exit 1
}

# Install Lighthouse CI
Write-Host "📦 Installing Lighthouse CI..." -ForegroundColor Blue
npm install -g @lhci/cli@latest

# Verify Lighthouse CI installation
try {
    $lhciVersion = lhci --version
    if ($LASTEXITCODE -ne 0) {
        throw "Lighthouse CI installation failed"
    }
    Write-Host "✅ Lighthouse CI installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Lighthouse CI installation failed" -ForegroundColor Red
    exit 1
}

# Install project dependencies
Write-Host "📦 Installing project dependencies..." -ForegroundColor Blue
npm install

# Test Lighthouse CLI
Write-Host "🧪 Testing Lighthouse CLI..." -ForegroundColor Blue
lighthouse --version

# Test Lighthouse CI
Write-Host "🧪 Testing Lighthouse CI..." -ForegroundColor Blue
lhci --version

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Blue
    Copy-Item "env.example" ".env"
    Write-Host "⚠️  Please update .env file with your actual API keys and configuration" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Lighthouse CLI setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env file with your API keys" -ForegroundColor White
Write-Host "2. Test with: npm run lighthouse:test" -ForegroundColor White
Write-Host "3. Run audit with: npm run lighthouse:audit" -ForegroundColor White
Write-Host "4. Run CI with: npm run lighthouse:ci" -ForegroundColor White
Write-Host ""
Write-Host "For more information, visit:" -ForegroundColor Cyan
Write-Host "  - https://developer.chrome.com/docs/lighthouse/overview" -ForegroundColor White
Write-Host "  - https://github.com/GoogleChrome/lighthouse-ci" -ForegroundColor White
