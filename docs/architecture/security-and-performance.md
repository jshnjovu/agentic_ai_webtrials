# Security and Performance

## Security Requirements

**Frontend Security:**
- **CSP Headers:** `default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.supabase.co; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https://api.supabase.co https://api.openai.com`
- **XSS Prevention:** React's built-in XSS protection, Content Security Policy headers, input sanitization using DOMPurify for user-generated content
- **Secure Storage:** Sensitive tokens stored in secure httpOnly cookies, session data in Supabase Auth, no localStorage for sensitive data

**Backend Security:**
- **Input Validation:** Pydantic models with comprehensive validation, SQL injection prevention through SQLAlchemy ORM, file upload restrictions and scanning
- **Rate Limiting:** 100 requests per minute per IP for general endpoints, 10 requests per minute for processing runs, 1000 requests per hour for authenticated users
- **CORS Policy:** `allowed_origins=['https://leadgen.vercel.app', 'https://leadgen-staging.vercel.app'], allowed_methods=['GET', 'POST', 'PUT', 'DELETE'], allowed_headers=['*'], allow_credentials=true`

**Authentication Security:**
- **Token Storage:** JWT tokens in secure httpOnly cookies with SameSite=Strict, automatic token refresh, 24-hour expiration
- **Session Management:** Supabase Auth with Row Level Security, automatic session cleanup, concurrent session limits
- **Password Policy:** Minimum 12 characters, mixed case, numbers, special characters, bcrypt hashing with salt rounds=12

## Performance Optimization

**Frontend Performance:**
- **Bundle Size Target:** < 500KB initial bundle, < 1MB total JavaScript, code splitting by route and feature
- **Loading Strategy:** Server-side rendering for initial page load, progressive enhancement for real-time features, lazy loading for non-critical components
- **Caching Strategy:** Static assets cached for 1 year, API responses cached for 5 minutes, Supabase real-time subscriptions with local state optimization

**Backend Performance:**
- **Response Time Target:** < 200ms for API endpoints, < 2000ms for processing initiation, < 60s for complete workflow processing
- **Database Optimization:** Connection pooling (20 connections, 30 overflow), query optimization with proper indexing, N+1 query prevention
- **Caching Strategy:** Redis caching for external API responses (1 hour TTL), business data caching (15 minutes TTL), rate limiting state in Redis

---
