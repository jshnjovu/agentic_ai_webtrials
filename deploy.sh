#!/bin/bash

echo "🚀 Deploying Agentic AI WebTrials to Vercel"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI is not installed. Installing now..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    print_warning "Not logged in to Vercel. Please login first:"
    vercel login
fi

echo ""
print_status "Starting deployment process..."

# Deploy Frontend
echo ""
print_status "Deploying Frontend (Next.js)..."
cd frontend

if git diff --quiet; then
    print_status "No changes to commit in frontend"
else
    print_status "Committing frontend changes..."
    git add .
    git commit -m "Deploy frontend to Vercel"
    git push origin main
fi

print_status "Frontend deployment triggered via Git push"
print_status "Check Vercel dashboard for deployment status"

# Deploy Backend
echo ""
print_status "Deploying Backend (FastAPI)..."
cd ../backend

print_status "Running Vercel deployment..."
vercel --prod

echo ""
print_status "Deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Test your API endpoints"
echo "3. Update frontend to use new backend URL"
echo ""
echo "🔗 Useful Commands:"
echo "- Check deployment status: vercel ls"
echo "- View logs: vercel logs [project-url]"
echo "- Redeploy: vercel --prod"
echo ""
echo "📚 Full deployment guide: DEPLOYMENT_GUIDE.md"
