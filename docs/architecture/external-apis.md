# External APIs

## Google Places API
- **Purpose:** Primary business discovery source for local business data with comprehensive contact information and geographic accuracy
- **Base URL:** https://maps.googleapis.com/maps/api/place/
- **Authentication:** API Key in query parameter or header
- **Rate Limits:** 1,000 requests per day (free tier), up to 100,000 requests per day (paid)
- **Key Endpoints Used:** `/textsearch/json`, `/details/json`, `/photo`

## Yelp Fusion API
- **Purpose:** Secondary business discovery and validation source providing review data, operating hours, and additional contact enrichment
- **Base URL:** https://api.yelp.com/v3/
- **Authentication:** Bearer token in Authorization header
- **Rate Limits:** 5,000 API calls per day, 500 calls per hour
- **Key Endpoints Used:** `/businesses/search`, `/businesses/{id}`, `/businesses/{id}/reviews`

## PageSpeed Insights / Lighthouse API
- **Purpose:** Automated website performance, accessibility, SEO, and best practices evaluation providing objective scoring data
- **Base URL:** https://www.googleapis.com/pagespeedonline/v5/
- **Authentication:** API Key parameter
- **Rate Limits:** 25,000 requests per day, 240 requests per minute
- **Key Endpoints Used:** `/runPagespeed`

## OpenAI API
- **Purpose:** AI-powered content generation for demo websites and personalized outreach campaigns using GPT models
- **Base URL:** https://api.openai.com/v1/
- **Authentication:** Bearer token with API key
- **Rate Limits:** Varies by model and tier (typically 3,500 requests per minute for GPT-3.5)
- **Key Endpoints Used:** `/chat/completions`, `/embeddings`

## Vercel Deployment API
- **Purpose:** Automated static site deployment and hosting for generated demo websites with global CDN distribution
- **Base URL:** https://api.vercel.com/
- **Authentication:** Bearer token with team/personal token
- **Rate Limits:** 100 deployments per hour (Hobby), 3,000 per hour (Pro)
- **Key Endpoints Used:** `/v13/deployments`, `/v6/deployments/{id}`, `DELETE /v13/deployments/{id}`

## Bravo Email Service
- **Purpose:** Professional email delivery service for outreach campaigns with delivery tracking and bounce management
- **Key Endpoints Used:** `/send`, `/webhook`, `/status/{message_id}`

## TextBee API (WhatsApp/SMS)
- **Purpose:** Multi-channel messaging service for WhatsApp and SMS outreach with delivery confirmation and international support
- **Base URL:** https://api.textbee.dev/
- **Authentication:** API key in header
- **Key Endpoints Used:** `/v1/whatsapp/send`, `/v1/sms/send`, `/webhook/delivery`

## Google Sheets API
- **Purpose:** Optional cloud-based data export and real-time collaboration for processing results and campaign data
- **Base URL:** https://sheets.googleapis.com/v4/
- **Authentication:** OAuth 2.0 or Service Account credentials
- **Rate Limits:** 300 requests per minute per project, 100 requests per 100 seconds per user
- **Key Endpoints Used:** `/spreadsheets`, `/spreadsheets/{id}/values/{range}`, `/spreadsheets/{id}`

---
