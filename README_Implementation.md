# Agentic AI Trial Task – LeadGen Website Makeover Agent

## Overview
This project scaffold is for the trial task: Build an Agentic AI system that:
1. Asks for location
2. Asks for local niche
3. Discovers businesses in that niche & location and collects contact details
4. Scores each business's website against best web design practices
5. Generates a new website for low scoring sites
6. Hosts the generated website temporarily and returns a link
7. Saves all data to a sheet/CSV
8. Generates WhatsApp, Email, and SMS messages pitching the new website

**Note:** This scaffold includes backend (FastAPI) and frontend (Next.js) placeholders, plus utility scripts for CSV writing. Replace stubs with your working implementations.

---

## Structure
```
/backend      - FastAPI app, API endpoints, AI orchestration
/frontend     - Next.js app (basic UI for location/niche input, results view)
/data         - Sample CSV exports
/scripts      - Utility scripts (e.g., CSV writing, API client stubs)
README.md     - This file
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Yarn or npm
- (Optional) API keys for:
  - OpenAI / Anthropic Claude
  - Google Places API / Yelp Fusion
  - Vercel/Netlify deployment
  - Lighthouse CI (for scoring)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
yarn install  # or npm install
yarn dev      # or npm run dev
```

---

## Deliverables
- End-to-end working agent for **≤10 businesses**
- CSV or Google Sheet with results
- At least one hosted demo website link
- Outreach messages per business
- Loom video (≤5 min) walkthrough

---

## License
For trial evaluation purposes only.
