# 4. Technical Assumptions

## Repository Structure

```
/
├── backend/                 # FastAPI application
│   ├── main.py             # API endpoints and Pydantic models
│   ├── discovery/          # Business discovery modules
│   ├── scoring/            # Website evaluation systems
│   ├── generation/         # Demo site creation
│   ├── export/             # Data export handlers
│   ├── outreach/           # Message generation
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js application
│   ├── pages/              # React components and routing
│   ├── components/         # Reusable UI components
│   ├── styles/             # CSS and styling
│   └── package.json        # Node.js dependencies
├── data/                   # Export outputs
│   ├── csv/                # Timestamped CSV files
│   └── logs/               # Processing logs
├── templates/              # Website generation templates
├── docs/                   # Documentation
└── README.md               # Setup and run instructions
```

## Service Architecture

**Application Layer:**
- **FastAPI Backend**: RESTful API with Pydantic data validation
- **Next.js Frontend**: Server-side rendering with React components
- **Background Tasks**: Async processing for long-running operations

**Integration Layer:**
- **Google Places API**: Primary business discovery source
- **Yelp Fusion API**: Secondary discovery and validation source
- **Lighthouse CI**: Primary website scoring engine
- **Custom Heuristics**: Complementary scoring system
- **AI/LLM APIs**: Content generation and personalization

**Data Layer:**
- **Local CSV Storage**: Primary data persistence
- **Google Sheets API**: Optional cloud sync
- **Vercel Hosting**: Demo site deployment

## Technology Stack Details

**Backend Technologies:**
- **Python 3.10+**: Core runtime with async support
- **FastAPI**: High-performance API framework
- **Pydantic**: Data validation and serialization
- **Requests/aiohttp**: HTTP client libraries
- **Pandas**: Data manipulation and CSV export
- **Jinja2**: Template rendering for websites

**Frontend Technologies:**
- **Next.js 13+**: React framework with SSR
- **React 18+**: Component library
- **TypeScript**: Type safety and developer experience
- **Tailwind CSS**: Utility-first styling
- **React Hook Form**: Form management
- **SWR**: Data fetching and caching

**External Services:**
- **Vercel**: Application and demo site hosting
- **Google Cloud APIs**: Places, Sheets, PageSpeed Insights
- **Yelp Fusion API**: Business data and reviews
- **OpenAI/Claude/Gemini**: AI content generation
- **Lighthouse CI**: Website performance auditing

## Testing Requirements

**Backend Testing:**
- **Unit Tests**: pytest for individual functions and classes
- **Integration Tests**: API endpoint testing with test databases
- **API Tests**: External API integration validation with mocking
- **Performance Tests**: Load testing for concurrent operations

**Frontend Testing:**
- **Component Tests**: Jest and React Testing Library
- **E2E Tests**: Playwright for user workflow validation
- **Visual Tests**: Storybook for component documentation
- **Accessibility Tests**: axe-core integration

**Test Coverage Targets:**
- **Backend**: 80% code coverage minimum
- **Frontend**: 70% code coverage for business logic
- **Critical Path**: 95% coverage for core workflow

## Deployment Strategy

**Development Environment:**
- Local development with Docker Compose
- Hot reload for both backend and frontend
- Mock external APIs for offline development

**Staging Environment:**
- Vercel preview deployments
- Limited API quotas for testing
- Automated testing pipeline

**Production Environment:**
- Vercel production deployment
- Full API access and quotas
- Performance monitoring and alerting

---
