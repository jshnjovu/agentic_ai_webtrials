# 6. Epic Details

## Epic 1: Hybrid Discovery Foundation

**Epic Description:** Build a reliable business discovery system that uses dual sources (Google Places + Yelp Fusion) to find local businesses, validate their information, and enrich contact details for maximum data completeness.

**User Stories:**

**Story 1.1: API Authentication Setup**
- **As a** system administrator
- **I want** secure API key management for Google Places and Yelp Fusion
- **So that** the system can authenticate and access business data reliably

**Acceptance Criteria:**
- ✓ Environment variables configured for both API keys
- ✓ Authentication error handling with clear error messages
- ✓ Rate limiting configuration for both APIs
- ✓ Connection testing on system startup

**Story 1.2: Google Places Business Search**
- **As a** lead generation agent
- **I want** to search Google Places for businesses by location and niche
- **So that** I can discover local businesses with comprehensive data

**Acceptance Criteria:**
- ✓ Text search functionality with location and category filters
- ✓ Business data extraction (name, address, phone, website, rating)
- ✓ Geographic radius search support
- ✓ Result pagination handling (up to 10 businesses)
- ✓ Error handling for invalid locations or API failures

**Story 1.3: Yelp Fusion Business Search**
- **As a** lead generation agent  
- **I want** to search Yelp Fusion as a secondary source
- **So that** I can validate and enrich business information

**Acceptance Criteria:**
- ✓ Business search with location and category parameters
- ✓ Business details extraction including reviews and hours
- ✓ Photo and additional contact information retrieval
- ✓ Category mapping between Google and Yelp taxonomies
- ✓ Rate limiting compliance (5000 requests per day)

**Story 1.4: Data Merging and Deduplication**
- **As a** lead generation agent
- **I want** to merge business data from multiple sources
- **So that** I have complete, validated business profiles

**Acceptance Criteria:**
- ✓ Business matching algorithm using name + address similarity
- ✓ Contact information prioritization (prefer most complete data)
- ✓ Duplicate business detection and removal
- ✓ Data confidence scoring for merged records
- ✓ Manual review flagging for uncertain matches

## Epic 2: Intelligent Website Scoring

**Epic Description:** Create a comprehensive website evaluation system that combines Lighthouse API automation with custom heuristic analysis to provide reliable scoring with fallback options.

**User Stories:**

**Story 2.1: Lighthouse API Integration**
- **As a** website evaluator
- **I want** to run Lighthouse audits programmatically
- **So that** I can score websites on performance, accessibility, best practices, and SEO

**Acceptance Criteria:**
- ✓ Lighthouse CI configuration for automated audits
- ✓ Performance score extraction (Core Web Vitals)
- ✓ Accessibility audit results parsing
- ✓ SEO and best practices evaluation
- ✓ Timeout handling for slow websites (30 second limit)

**Story 2.2: Custom Heuristic Evaluation**
- **As a** website evaluator
- **I want** to analyze trust signals and CRO elements
- **So that** I can complement Lighthouse scores with business-focused metrics

**Acceptance Criteria:**
- ✓ Trust signal detection (HTTPS, privacy policy, contact info)
- ✓ Conversion optimization element identification (CTA buttons, forms)
- ✓ Mobile usability heuristics (viewport, touch targets)
- ✓ Content quality assessment (headings structure, alt text)
- ✓ Social proof element detection (testimonials, reviews)

**Story 2.3: Score Validation and Confidence**
- **As a** system operator
- **I want** cross-validation between scoring methods
- **So that** I can provide confidence ratings for audit results

**Acceptance Criteria:**
- ✓ Score consistency checking between Lighthouse and heuristics
- ✓ Confidence level assignment (high/medium/low)
- ✓ Discrepancy flagging for manual review
- ✓ Weighted final score calculation
- ✓ Issue prioritization ranking

**Story 2.4: Fallback Scoring System**
- **As a** system operator
- **I want** heuristic-only scoring when Lighthouse fails
- **So that** I can provide consistent evaluation coverage

**Acceptance Criteria:**
- ✓ Automatic fallback detection when Lighthouse fails
- ✓ Heuristic-only scoring algorithm (100-point scale)
- ✓ Reduced confidence indication for fallback scores
- ✓ Retry logic for temporary Lighthouse failures
- ✓ Detailed logging of fallback reasons

## Epic 3: Demo Site Generation Engine

**Epic Description:** Build an automated website generation system that creates professional, responsive demo sites for businesses with low scores, optimized for conversion and mobile-first design.

**User Stories:**

**Story 3.1: Website Template Design**
- **As a** demo site generator
- **I want** responsive HTML/CSS templates
- **So that** I can create professional-looking websites quickly

**Acceptance Criteria:**
- ✓ Mobile-first responsive design (breakpoints: 320px, 768px, 1024px)
- ✓ Core sections: hero, services, about, contact, map
- ✓ Call-to-action button prominence and conversion optimization
- ✓ Accessibility compliance (WCAG 2.1 AA)
- ✓ Fast loading performance (<3 seconds)

**Story 3.2: AI-Powered Content Generation**
- **As a** demo site generator
- **I want** to create business-specific content using AI
- **So that** demo sites feel personalized and relevant

**Acceptance Criteria:**
- ✓ Business description generation based on niche and location
- ✓ Service list creation appropriate for business type
- ✓ Contact information integration from discovery data
- ✓ Local SEO optimization (location keywords, schema markup)
- ✓ Content tone appropriate for target audience

**Story 3.3: Vercel Deployment Integration**
- **As a** demo site generator
- **I want** automated deployment to Vercel
- **So that** I can provide public URLs for demo sites

**Acceptance Criteria:**
- ✓ Vercel API integration for programmatic deployment
- ✓ Static site optimization and build process
- ✓ Custom domain or subdomain generation
- ✓ SSL certificate automatic provisioning
- ✓ Deployment status monitoring and error handling

**Story 3.4: Demo Site Tracking**
- **As a** system operator
- **I want** to track generated demo sites
- **So that** I can manage temporary hosting and provide analytics

**Acceptance Criteria:**
- ✓ Demo site URL generation and storage
- ✓ Creation timestamp and expiration tracking
- ✓ Basic analytics integration (page views, device types)
- ✓ Cleanup process for expired demos
- ✓ Performance monitoring for deployed sites

## Epic 4: Flexible Data Management

**Epic Description:** Implement a comprehensive data export system that supports both offline CSV files and optional cloud-based Google Sheets synchronization for maximum workflow flexibility.

**User Stories:**

**Story 4.1: CSV Export Foundation**
- **As a** lead generation user
- **I want** comprehensive CSV export functionality
- **So that** I can analyze and use business data offline

**Acceptance Criteria:**
- ✓ Complete data model export (20+ fields)
- ✓ Timestamped file naming for run organization
- ✓ Proper CSV formatting with headers and encoding (UTF-8)
- ✓ Data validation before export (required fields, format checking)
- ✓ Export progress indication for large datasets

**Story 4.2: Google Sheets Integration**
- **As a** collaborative team user
- **I want** optional Google Sheets sync
- **So that** I can share results in real-time with team members

**Acceptance Criteria:**
- ✓ Google Sheets API authentication and authorization
- ✓ Spreadsheet creation with proper formatting and headers
- ✓ Real-time data synchronization option
- ✓ Permission management for shared sheets
- ✓ Sync status indication and error handling

**Story 4.3: Run Tracking and Deduplication**
- **As a** system operator
- **I want** run tracking and duplicate prevention
- **So that** I can avoid processing the same businesses multiple times

**Acceptance Criteria:**
- ✓ Unique run ID generation for each processing session
- ✓ Business fingerprinting for duplicate detection
- ✓ Historical run data preservation
- ✓ Duplicate business flagging and skip logic
- ✓ Run statistics and summary reporting

**Story 4.4: Data Model Completeness**
- **As a** lead generation user
- **I want** comprehensive business data capture
- **So that** I have all information needed for outreach campaigns

**Acceptance Criteria:**
- ✓ Business details: name, niche, location, contact info, website
- ✓ Scoring breakdown: overall, performance, accessibility, SEO, trust, CRO
- ✓ Generated content: demo site URL, outreach messages
- ✓ Metadata: run ID, timestamp, confidence scores, notes
- ✓ Data completeness percentage calculation per record

## Epic 5: Outreach Campaign Generator

**Epic Description:** Create intelligent, personalized outreach message generation across multiple channels (Email, WhatsApp, SMS) using AI and business-specific context for maximum conversion potential.

**User Stories:**

**Story 5.1: Email Campaign Generation**
- **As a** sales outreach user
- **I want** personalized email templates with subject lines
- **So that** I can conduct professional email campaigns

**Acceptance Criteria:**
- ✓ Subject line generation with personalization variables
- ✓ Professional email body with business-specific context
- ✓ Demo site URL integration with clear value proposition
- ✓ Top 3 website issues highlighting for credibility
- ✓ Call-to-action optimization for response generation

**Story 5.2: WhatsApp Message Optimization**
- **As a** mobile-first outreach user
- **I want** WhatsApp-optimized message content
- **So that** I can engage prospects on their preferred mobile platform

**Acceptance Criteria:**
- ✓ Concise message format optimized for mobile reading
- ✓ Casual but professional tone appropriate for WhatsApp
- ✓ Demo site URL with mobile-friendly preview
- ✓ Clear call-to-action for quick response
- ✓ Emoji usage guidelines for engagement without unprofessionalism

**Story 5.3: SMS Content Generation**
- **As a** direct outreach user
- **I want** SMS messages within character limits
- **So that** I can reach prospects via text messaging

**Acceptance Criteria:**
- ✓ 280-character maximum message length
- ✓ Essential information prioritization (business name, demo URL)
- ✓ Clear call-to-action within character constraints
- ✓ URL shortening for demo site links
- ✓ Opt-out compliance and professional tone

**Story 5.4: AI-Powered Personalization**
- **As a** outreach effectiveness optimizer
- **I want** AI-driven message personalization
- **So that** each message feels relevant and increases response rates

**Acceptance Criteria:**
- ✓ Business niche-specific language and terminology
- ✓ Location-based personalization (local references)
- ✓ Website issue prioritization based on business type
- ✓ Value proposition customization per industry
- ✓ Contact name integration when available

---
