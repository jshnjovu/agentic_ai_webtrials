# Deployment Architecture

## Deployment Strategy

**Frontend Deployment:**
- **Platform:** Vercel (Next.js optimized hosting)
- **Build Command:** `npm run build --workspace=apps/web`
- **Output Directory:** `apps/web/.next`
- **CDN/Edge:** Vercel Edge Network with global distribution

**Backend Deployment:**
- **Platform:** Vercel Serverless Functions (FastAPI adapter)
- **Build Command:** `npm run build --workspace=apps/api`
- **Deployment Method:** Serverless functions with automatic scaling

**Database Deployment:**
- **Platform:** Supabase (Managed PostgreSQL)
- **Migration Strategy:** Automated migrations via CI/CD
- **Backup Strategy:** Automatic daily backups with 30-day retention

## Environments

| Environment | Frontend URL | Backend URL | Purpose |
|-------------|--------------|-------------|---------|
| Development | http://localhost:3000 | http://localhost:8000 | Local development and testing |
| Staging | https://leadgen-staging.vercel.app | https://leadgen-staging.vercel.app/api | Pre-production testing and demos |
| Production | https://leadgen.vercel.app | https://leadgen.vercel.app/api | Live production environment |

## CI/CD Pipeline Configuration

### GitHub Actions Workflows

**.github/workflows/ci.yaml** - Continuous Integration
```yaml
name: Continuous Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run frontend unit tests
        run: npm run test:web
        
      - name: Run frontend integration tests
        run: npm run test:web:integration
        
      - name: Build frontend application
        run: npm run build --workspace=apps/web
        
      - name: Upload frontend build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: frontend-build
          path: apps/web/.next/
          retention-days: 7

  backend-tests:
    name: Backend Tests
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: leadgen_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: latest
          virtualenvs-create: true
          virtualenvs-in-project: true
          
      - name: Cache Poetry dependencies
        uses: actions/cache@v3
        with:
          path: apps/api/.venv
          key: poetry-${{ runner.os }}-${{ hashFiles('apps/api/poetry.lock') }}
          
      - name: Install backend dependencies
        working-directory: apps/api
        run: poetry install --with dev,test
        
      - name: Run database migrations
        working-directory: apps/api
        run: |
          poetry run alembic upgrade head
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/leadgen_test
          
      - name: Run backend unit tests
        working-directory: apps/api
        run: poetry run pytest tests/unit/ -v --cov=src --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/leadgen_test
          REDIS_URL: redis://localhost:6379
          
      - name: Run backend integration tests
        working-directory: apps/api
        run: poetry run pytest tests/integration/ -v
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/leadgen_test
          REDIS_URL: redis://localhost:6379
          
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: apps/api/coverage.xml
          flags: backend
          
  e2e-tests:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    needs: [frontend-tests, backend-tests]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install dependencies
        run: |
          npm ci
          cd apps/api && poetry install
          
      - name: Install Playwright
        run: npx playwright install --with-deps
        
      - name: Start services for E2E testing
        run: |
          npm run dev:api &
          npm run dev:web &
          sleep 30  # Wait for services to start
          
      - name: Run E2E tests
        run: npm run test:e2e
        
      - name: Upload E2E test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: e2e-test-results
          path: test-results/
          retention-days: 7

  security-audit:
    name: Security Audit
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          
      - name: Run npm security audit
        run: npm audit --audit-level=moderate
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install safety
        run: pip install safety
        
      - name: Run Python security audit
        working-directory: apps/api
        run: safety check --file requirements.txt
```

**.github/workflows/deploy-staging.yaml** - Staging Deployment
```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]
  workflow_dispatch:

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID_STAGING }}

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: |
          npm run test:web
          npm run test:api
          
      - name: Build applications
        run: |
          npm run build --workspace=apps/web
          npm run build --workspace=apps/api
        env:
          NEXT_PUBLIC_API_BASE_URL: https://leadgen-staging.vercel.app/api
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.STAGING_SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.STAGING_SUPABASE_ANON_KEY }}
          
      - name: Install Vercel CLI
        run: npm install --global vercel@latest
        
      - name: Pull Vercel environment information
        run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}
        
      - name: Deploy to Vercel
        id: deploy
        run: |
          vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }} > deployment-url.txt
          echo "DEPLOYMENT_URL=$(cat deployment-url.txt)" >> $GITHUB_OUTPUT
          
      - name: Promote to staging alias
        run: vercel alias $(cat deployment-url.txt) leadgen-staging.vercel.app --token=${{ secrets.VERCEL_TOKEN }}
        
      - name: Run staging health checks
        run: |
          sleep 30  # Wait for deployment to be fully ready
          npm run health-check -- --url https://leadgen-staging.vercel.app
          
      - name: Run staging smoke tests
        run: npm run test:smoke -- --base-url https://leadgen-staging.vercel.app
        
      - name: Notify deployment status
        uses: 8398a7/action-slack@v3
        if: always()
        with:
          status: ${{ job.status }}
          text: 'Staging deployment ${{ job.status }}: ${{ steps.deploy.outputs.DEPLOYMENT_URL }}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**.github/workflows/deploy-production.yaml** - Production Deployment
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  release:
    types: [published]
  workflow_dispatch:

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID_PRODUCTION }}

jobs:
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run comprehensive test suite
        run: |
          npm run test:web
          npm run test:api
          npm run test:integration
          npm run test:e2e
          
      - name: Build applications for production
        run: |
          npm run build --workspace=apps/web
          npm run build --workspace=apps/api
        env:
          NEXT_PUBLIC_API_BASE_URL: https://leadgen.vercel.app/api
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.PRODUCTION_SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.PRODUCTION_SUPABASE_ANON_KEY }}
          NODE_ENV: production
          
      - name: Install Vercel CLI
        run: npm install --global vercel@latest
        
      - name: Pull Vercel environment information
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
        
      - name: Deploy to Vercel
        id: deploy
        run: |
          vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }} > deployment-url.txt
          echo "DEPLOYMENT_URL=$(cat deployment-url.txt)" >> $GITHUB_OUTPUT
          
      - name: Run production health checks
        run: |
          sleep 60  # Wait for deployment to be fully ready
          npm run health-check -- --url https://leadgen.vercel.app
          
      - name: Run production smoke tests
        run: npm run test:smoke -- --base-url https://leadgen.vercel.app
        
      - name: Create deployment tag
        run: |
          git tag "deployment-$(date +'%Y%m%d-%H%M%S')"
          git push origin --tags
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Notify deployment success
        uses: 8398a7/action-slack@v3
        if: success()
        with:
          status: success
          text: '🚀 Production deployment successful: https://leadgen.vercel.app'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          
      - name: Notify deployment failure
        uses: 8398a7/action-slack@v3
        if: failure()
        with:
          status: failure
          text: '❌ Production deployment failed! Check GitHub Actions for details.'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Required GitHub Secrets

**Repository Secrets:**
```bash