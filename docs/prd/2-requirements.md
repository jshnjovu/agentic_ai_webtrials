# 2. Requirements

## Functional Requirements (FR)

**FR-1: Hybrid Business Discovery Module**
- **FR-1.1:** Accept location and niche input through user interface
- **FR-1.2:** Execute Google Places API search for business discovery (primary source)
- **FR-1.3:** Execute Yelp Fusion API search for business discovery (secondary source)
- **FR-1.4:** Cross-validate contact information extraction between sources
- **FR-1.5:** Implement data merging and deduplication logic based on business name + address
- **FR-1.6:** Enrich business profiles to achieve 85% average contact field completion
- **FR-1.7:** Limit discovery to maximum 10 businesses per trial run

**FR-2: Hybrid Website Scoring System**
- **FR-2.1:** Execute Lighthouse API audit for primary scoring (Performance, Accessibility, Best Practices, SEO - 80 points max)
- **FR-2.2:** Execute custom heuristic evaluation (Trust signals, CRO elements, mobile UX - 20 points max)
- **FR-2.3:** Implement cross-validation layer to flag scoring inconsistencies
- **FR-2.4:** Provide fallback scoring when Lighthouse API fails (heuristics only, 100 points scale)
- **FR-2.5:** Identify and prioritize top 3 improvement issues per website
- **FR-2.6:** Generate confidence scoring (high/medium/low) based on evaluation methods used

**FR-3: Demo Website Generation Engine**
- **FR-3.1:** Generate clean, minimal websites for businesses scoring <70
- **FR-3.2:** Include core sections: hero (value proposition), services, CTA, contact form, map integration
- **FR-3.3:** Implement responsive, mobile-first design approach
- **FR-3.4:** Use AI/LLM for dynamic content generation based on business context
- **FR-3.5:** Generate static sites optimized for Vercel hosting
- **FR-3.6:** Complete generation and deployment within 2 minutes per site

**FR-4: Flexible Data Export System**
- **FR-4.1:** Generate timestamped CSV files as primary export method
- **FR-4.2:** Implement optional Google Sheets sync for real-time collaboration
- **FR-4.3:** Support comprehensive data model with 20+ fields including:
  - Business details: name, niche, location, contact info, website, address
  - Scoring: overall, performance, accessibility, SEO, trust, CRO breakdown
  - Generated content: demo site URL, outreach messages
  - Metadata: run ID, timestamp, notes
- **FR-4.4:** Implement run tracking and duplicate prevention across sessions

**FR-5: Personalized Outreach Generation**
- **FR-5.1:** Generate personalized email templates with subject line and body content
- **FR-5.2:** Create WhatsApp message content optimized for mobile engagement
- **FR-5.3:** Generate SMS campaign content within 280-character limit
- **FR-5.4:** Implement AI-powered personalization using business-specific data
- **FR-5.5:** Include variable substitution for business name, location, contact name, demo URL, top issues

## Non-Functional Requirements (NFR)

**NFR-1: Performance Requirements**
- **NFR-1.1:** Complete 10-business processing cycle within 15 minutes total
- **NFR-1.2:** Maintain 1-2 requests per second rate limiting across all APIs
- **NFR-1.3:** Implement exponential backoff with jitter for API retry logic
- **NFR-1.4:** Generate and deploy static sites within 2 minutes per site
- **NFR-1.5:** Support concurrent processing where API limits allow

**NFR-2: Reliability Requirements**
- **NFR-2.1:** Achieve 95%+ success rate through hybrid system design
- **NFR-2.2:** Implement graceful API failure handling with automatic fallbacks
- **NFR-2.3:** Provide data validation and consistency checks across all modules
- **NFR-2.4:** Handle network timeouts and service interruptions without data loss
- **NFR-2.5:** Log all operations for debugging and audit purposes

**NFR-3: Scalability Constraints (Trial Phase)**
- **NFR-3.1:** Maximum 10 businesses per trial run for resource management
- **NFR-3.2:** Use public data sources only (respect robots.txt and Terms of Service)
- **NFR-3.3:** Static hosting only for demo sites (no dynamic server requirements)
- **NFR-3.4:** Local processing with optional cloud sync capabilities

**NFR-4: Integration Requirements**
- **NFR-4.1:** Support OpenAI-compatible LLM APIs (OpenAI, Anthropic Claude, Gemini, Deepseek)
- **NFR-4.2:** Integrate Vercel deployment API for demo site hosting
- **NFR-4.3:** Connect Google Places, Yelp Fusion, and Lighthouse CI APIs
- **NFR-4.4:** Maintain API key security and proper authentication flows

**NFR-5: Usability Requirements**
- **NFR-5.1:** Provide simple web UI for location and niche input
- **NFR-5.2:** Display real-time progress during processing
- **NFR-5.3:** Present results in clear, actionable format
- **NFR-5.4:** Support both technical and business user personas

---
