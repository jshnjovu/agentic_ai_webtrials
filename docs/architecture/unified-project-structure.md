# Unified Project Structure

```plaintext
leadgen-makeover-agent/
├── .github/                        # CI/CD workflows
│   └── workflows/
│       ├── ci.yaml                 # Test and build pipeline
│       ├── deploy-staging.yaml     # Staging deployment
│       └── deploy-production.yaml  # Production deployment
├── apps/                           # Application packages
│   ├── web/                        # Next.js Frontend Application
│   │   ├── src/
│   │   │   ├── components/         # React components
│   │   │   ├── pages/              # Next.js pages/routing
│   │   │   ├── hooks/              # Custom React hooks
│   │   │   ├── services/           # API client services
│   │   │   ├── stores/             # Zustand state management
│   │   │   ├── styles/             # Global styles and themes
│   │   │   ├── utils/              # Frontend utilities
│   │   │   └── lib/                # Configuration and setup
│   │   ├── public/                 # Static assets
│   │   ├── tests/                  # Frontend tests
│   │   ├── next.config.js          # Next.js configuration
│   │   ├── tailwind.config.js      # Tailwind CSS config
│   │   ├── tsconfig.json           # TypeScript configuration
│   │   └── package.json            # Frontend dependencies
│   └── api/                        # FastAPI Backend Application
│       ├── src/
│       │   ├── main.py             # FastAPI app entry point
│       │   ├── core/               # Core application logic
│       │   ├── api/                # API route definitions
│       │   ├── agents/             # AI Agent implementations
│       │   ├── services/           # Business logic services
│       │   ├── models/             # SQLAlchemy database models
│       │   ├── schemas/            # Pydantic request/response schemas
│       │   ├── repositories/       # Data access layer
│       │   └── utils/              # Backend utilities
│       ├── tests/                  # Backend tests
│       ├── alembic/                # Database migrations
│       ├── requirements/           # Dependency management
│       ├── Dockerfile              # Container configuration
│       ├── .env.example            # Environment template
│       └── pyproject.toml          # Python project config
├── packages/                       # Shared packages
│   ├── shared/                     # Shared types and utilities
│   │   ├── src/
│   │   │   ├── types/              # TypeScript/Python shared types
│   │   │   ├── constants/          # Shared constants
│   │   │   ├── utils/              # Shared utility functions
│   │   │   └── schemas/            # Shared validation schemas
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── ui/                         # Shared UI component library
│   │   ├── src/
│   │   │   ├── components/         # Reusable UI components
│   │   │   ├── hooks/              # Shared React hooks
│   │   │   ├── styles/             # Shared styles
│   │   │   └── utils/              # UI utilities
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── config/                     # Shared configuration
│       ├── eslint/                 # ESLint configurations
│       ├── typescript/             # TypeScript configurations
│       ├── jest/                   # Jest testing configurations
│       └── tailwind/               # Tailwind CSS configurations
├── templates/                      # Website generation templates
│   ├── base/                       # Base template structure
│   ├── themes/                     # Different visual themes
│   └── assets/                     # Template assets
├── infrastructure/                 # Infrastructure as Code
│   ├── vercel/                     # Vercel deployment config
│   ├── supabase/                   # Supabase configuration
│   └── github-actions/             # CI/CD configuration
├── scripts/                        # Build and deployment scripts
├── data/                           # Data storage and exports
│   ├── exports/                    # Generated CSV exports
│   ├── logs/                       # Application logs
│   └── cache/                      # Temporary cache files
├── docs/                           # Documentation
│   ├── prd.md                      # Product Requirements Document
│   ├── architecture.md             # This architecture document
│   ├── api/                        # API documentation
│   ├── agents/                     # Agent documentation
│   ├── deployment/                 # Deployment guides
│   └── troubleshooting/            # Troubleshooting guides
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore patterns
├── package.json                    # Root package.json (workspace config)
├── package-lock.json               # Lock file for dependencies
├── tsconfig.json                   # Root TypeScript configuration
├── turbo.json                      # Turborepo configuration
├── docker-compose.yml              # Local development environment
├── docker-compose.prod.yml         # Production docker setup
└── README.md                       # Project documentation
```

---
