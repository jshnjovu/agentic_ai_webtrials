# Components

## Agent Orchestrator

**Responsibility:** Central coordination hub that manages the parallel execution of all AI agents, handles workflow state transitions, implements retry logic, and provides real-time progress updates through Supabase.

**Key Interfaces:**
- `POST /api/processing-runs` - Initiates new processing workflow
- `WebSocket /api/processing-runs/{id}/progress` - Real-time status broadcasting  
- `AgentManager.orchestrate(run_config)` - Internal agent coordination
- `ProgressTracker.update(run_id, status, metrics)` - Status management

**Dependencies:** Supabase (state persistence), All AI Agents (coordination), WebSocket Manager (progress broadcasting)

**Technology Stack:** FastAPI with asyncio for concurrent agent management, Supabase for state persistence, custom orchestration logic with exponential backoff and circuit breakers.

## Business Discovery Agent

**Responsibility:** Parallel business discovery using Google Places API and Yelp Fusion API with intelligent data merging, deduplication, and contact enrichment to achieve 85%+ field completion rates.

**Key Interfaces:**
- `DiscoveryAgent.discover_businesses(location, niche, max_count)` - Main discovery method
- `GooglePlacesClient.search(query, location)` - Google Places integration
- `YelpFusionClient.search(term, location)` - Yelp API integration
- `DataMerger.merge_and_deduplicate(google_data, yelp_data)` - Data consolidation

**Dependencies:** Google Places API, Yelp Fusion API, Business Database Models, Rate Limiter

**Technology Stack:** Python asyncio for parallel API calls, Pydantic for data validation, custom fuzzy matching for deduplication, exponential backoff with jitter for API reliability.

## Website Scoring Agent  

**Responsibility:** Hybrid website evaluation combining Lighthouse API automation with custom heuristic analysis, providing fallback scoring mechanisms and detailed improvement recommendations with confidence ratings.

**Key Interfaces:**
- `ScoringAgent.score_website(website_url, business_context)` - Primary scoring method
- `LighthouseClient.audit(url)` - Performance/accessibility/SEO scoring
- `HeuristicAnalyzer.evaluate(website_html, business_type)` - Trust/CRO scoring
- `ScoreValidator.validate_and_merge(lighthouse_data, heuristic_data)` - Hybrid scoring

**Dependencies:** Lighthouse CI API, Website Scoring Database Models, HTTP Client for website fetching

**Technology Stack:** Lighthouse CLI integration, BeautifulSoup for HTML parsing, custom scoring algorithms with weighted averages, timeout handling for slow websites.

## Demo Site Generation Agent

**Responsibility:** AI-powered website generation using business context and scoring data, creating responsive static sites with Jinja2 templates, and automated Vercel deployment with performance tracking.

**Key Interfaces:**
- `GenerationAgent.generate_site(business_data, score_data, template_type)` - Site generation
- `ContentGenerator.create_content(business_context, ai_model)` - AI content creation
- `TemplateRenderer.render(template, content_data)` - Static site assembly
- `VercelDeployer.deploy(site_files, domain_config)` - Hosting deployment

**Dependencies:** OpenAI/LLM APIs, Jinja2 Templates, Generated Site Database Models, Vercel Deployment API

**Technology Stack:** Jinja2 templating engine, OpenAI SDK for content generation, Vercel CLI for deployment automation, static site optimization with Tailwind CSS.

## Outreach Campaign Agent

**Responsibility:** Multi-channel personalized message generation using AI and business-specific context, with delivery tracking integration for Email (Bravo), WhatsApp/SMS (TextBee), and webhook callback processing.

**Key Interfaces:**
- `OutreachAgent.generate_campaign(business_data, demo_url, tone)` - Campaign creation
- `MessagePersonalizer.personalize(template, business_context, ai_model)` - AI personalization
- `DeliveryManager.send_messages(campaign_data, channels)` - Multi-channel sending
- `CallbackHandler.process_delivery_status(webhook_data)` - Delivery confirmation

**Dependencies:** OpenAI/LLM APIs, Bravo Email Service, TextBee API, Outreach Campaign Database Models, Webhook System

**Technology Stack:** OpenAI SDK for message personalization, HTTP clients for delivery services, webhook processing with FastAPI, delivery status tracking with real-time updates.

---
