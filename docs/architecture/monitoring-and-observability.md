# Monitoring and Observability

## Monitoring Stack

- **Frontend Monitoring:** Vercel Analytics + Sentry for error tracking and performance monitoring
- **Backend Monitoring:** Structured logging with JSON format, custom metrics via FastAPI middleware
- **Error Tracking:** Sentry integration for both frontend and backend error capture and alerting
- **Performance Monitoring:** Custom dashboards for agent execution times, API response times, external service health

## Key Metrics

**Frontend Metrics:**
- Core Web Vitals (LCP, FID, CLS)
- JavaScript errors and error rates
- API response times from frontend perspective  
- User interactions and processing run completion rates
- Real-time connection stability and reconnection frequency

**Backend Metrics:**
- Request rate and error rates per endpoint
- Processing run success/failure rates
- Individual agent execution times and success rates
- External API response times and failure rates
- Database query performance and connection pool utilization
- WebSocket connection counts and message throughput

---
