# Introduction

This document outlines the complete fullstack architecture for the **LeadGen Website Makeover Agent**, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

## Starter Template or Existing Project

**Project Foundation:** This is a **hybrid approach** - starting with an existing project scaffold that provides basic structure, but requiring significant architectural decisions and implementation.

**Current Foundation:**
- **Existing Structure**: Backend (FastAPI) + Frontend (Next.js) scaffold with placeholder implementations
- **Pre-configured Integrations**: Vercel deployment, basic CSV export functionality
- **Technology Constraints**: Must work with existing FastAPI/Next.js foundation
- **API Access**: Confirmed access to Vercel, Google APIs, Yelp, WhatsApp/Facebook APIs, Bravo Email Service, TextBee.dev

**Architectural Implications:**
- Must respect existing FastAPI + Next.js foundation
- Can enhance but not replace core framework choices
- Need to integrate with specified external services
- Focus on implementing the agentic AI orchestration layer

---
