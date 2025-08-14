# Coding Standards

## Critical Fullstack Rules

- **Type Sharing:** Always define types in packages/shared and import from @leadgen/shared/types - never duplicate interface definitions between frontend and backend
- **API Calls:** Never make direct HTTP calls - use the centralized API client service with proper error handling and retry logic
- **Environment Variables:** Access only through config objects, never process.env directly - use src/core/config.py for backend and lib/config.ts for frontend
- **Error Handling:** All API routes must use the standard error handler with proper HTTP status codes and structured error responses
- **State Updates:** Never mutate state directly - use proper state management patterns (Zustand actions for frontend, immutable updates for backend)
- **Database Access:** Always use repository pattern - never write raw SQL queries in business logic, use the repository layer
- **External API Integration:** All external API calls must include circuit breaker pattern and exponential backoff retry logic
- **Real-time Updates:** Use Supabase Realtime subscriptions only - never implement custom WebSocket connections
- **Agent Orchestration:** All AI agents must extend BaseAgent class and implement proper error recovery and progress reporting
- **Authentication:** Use Supabase Auth tokens consistently - never implement custom authentication logic
- **File Uploads:** All file operations must use Vercel Blob storage - never store files locally or in database
- **Logging:** Use structured logging with consistent format - include runId, businessId, and agentName in all log entries

## Naming Conventions

| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| Components | PascalCase | - | `ProcessingDashboard.tsx` |
| Hooks | camelCase with 'use' | - | `useProcessingProgress.ts` |
| API Routes | - | kebab-case | `/api/v1/processing-runs` |
| Database Tables | - | snake_case | `processing_runs` |
| Environment Variables | SCREAMING_SNAKE_CASE | SCREAMING_SNAKE_CASE | `GOOGLE_PLACES_API_KEY` |
| Agent Classes | PascalCase with 'Agent' | PascalCase with 'Agent' | `DiscoveryAgent` |
| Service Classes | PascalCase with 'Service' | PascalCase with 'Service' | `ProgressService` |
| Repository Classes | PascalCase with 'Repository' | PascalCase with 'Repository' | `BusinessRepository` |
| Constants | SCREAMING_SNAKE_CASE | SCREAMING_SNAKE_CASE | `MAX_BUSINESSES_PER_RUN` |
| Utility Functions | camelCase | snake_case | `formatBusinessData` / `format_business_data` |

---
