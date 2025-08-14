# Testing Strategy

## Testing Pyramid

```
                    E2E Tests
                 /              \
            Integration Tests
           /                    \
      Frontend Unit       Backend Unit
```

**Test Distribution:**
- **Frontend Unit Tests**: 60% of total tests
- **Backend Unit Tests**: 25% of total tests  
- **Integration Tests**: 10% of total tests
- **E2E Tests**: 5% of total tests

## Test Organization

**Frontend Tests:**
```
apps/web/tests/
├── __mocks__/                      # Mock implementations
├── components/                     # Component tests
├── hooks/                          # Custom hook tests
├── services/                       # Service layer tests
├── utils/                          # Utility function tests
└── e2e/                           # End-to-end tests
```

**Backend Tests:**
```
apps/api/tests/
├── conftest.py                     # Test configuration and fixtures
├── unit/                          # Unit tests
│   ├── test_agents/               # AI Agent tests
│   ├── test_services/             # Service layer tests
│   ├── test_models/               # Database model tests
│   └── test_utils/                # Utility tests
├── integration/                   # Integration tests
│   ├── test_api/                  # API endpoint tests
│   ├── test_external_apis/        # External API integration
│   └── test_database/             # Database integration
└── e2e/                          # End-to-end workflow tests
```

---
