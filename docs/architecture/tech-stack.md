# Tech Stack

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Language | TypeScript | 5.3+ | Type-safe frontend development | Shared types between frontend/backend, AI agent interfaces need strong typing |
| Frontend Framework | Next.js | 14.0+ | React framework with SSR | Existing scaffold foundation, Vercel integration, Edge Runtime support |
| UI Component Library | shadcn/ui + Radix | Latest | Accessible component system | Professional UI for business users, accessibility compliance |
| State Management | Zustand + React Query | Latest | Client state + server state | Lightweight for real-time progress, React Query perfect for API orchestration |
| Backend Language | Python | 3.11+ | AI/ML ecosystem compatibility | Existing FastAPI foundation, rich AI libraries, async support |
| Backend Framework | FastAPI | 0.104+ | High-performance async API | Existing scaffold, automatic OpenAPI docs, WebSocket support |
| API Style | REST + WebSocket | HTTP/1.1 | Real-time + standard APIs | WebSocket for progress tracking, REST for CRUD operations |
| Database | Supabase PostgreSQL | Latest | Real-time capable database | Real-time subscriptions, ACID compliance, automatic API generation |
| Cache | Vercel KV (Redis) | Latest | API response caching | Distributed caching for API rate limiting, session storage |
| File Storage | Vercel Blob | Latest | Generated sites + assets | Static site artifacts, CSV exports, temporary file storage |
| Authentication | Supabase Auth | Latest | User session management | Integrated with database, supports API keys, session tracking |
| Frontend Testing | Vitest + Testing Library | Latest | Component and integration testing | Faster than Jest, better TypeScript support, aligned with Vite ecosystem |
| Backend Testing | pytest + httpx | Latest | API and agent testing | Async test support, FastAPI testing utilities, AI agent mocking |
| E2E Testing | Playwright | Latest | End-to-end workflow validation | Cross-browser testing, AI agent orchestration testing |
| Build Tool | Vite | Latest | Fast frontend builds | Next.js uses Turbopack, Vite for standalone tools |
| Bundler | Turbopack (Next.js) | Built-in | Next.js optimization | Built into Next.js 14+, optimized for development speed |
| IaC Tool | Vercel CLI | Latest | Deployment automation | Infrastructure as code for Vercel deployments |
| CI/CD | GitHub Actions | Latest | Automated testing and deployment | Repository integration, Vercel deployment actions |
| Monitoring | Vercel Analytics + Sentry | Latest | Performance and error tracking | Built-in Vercel integration, AI agent error tracking |
| Logging | Vercel Logs + Supabase Logs | Built-in | Application and database logging | Centralized logging for debugging agent workflows |
| CSS Framework | Tailwind CSS | 3.3+ | Utility-first styling | Existing foundation, rapid UI development, consistent design |

---
