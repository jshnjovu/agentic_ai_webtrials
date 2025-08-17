Below are **seven bite-sized user stories** (BDD style) that exercise **every spec’d feature** of the LeadGen Website Makeover Agent.  
Each story contains:

- **As… / I want… / So that…**  
- **  data &   back-end stubs** you can drop into `/frontend/__tests__` for Cypress or Playwright.  
- **Expected UI behaviours** (progress spinners, retry banners, “blocked” toasts, etc.).

Copy-paste the stubs to build **automated or manual QA scripts**.

---

### Story 1  Discovery Happy Path
**As** a growth-agency intern  
**I want** to type “Austin, TX” + “Vegan restaurants”  
**So that** the agent discovers exactly 10 businesses.

####   API stub (`GET /api/discover`)
```json
["Scraping Google Places…","Found 3","Found 7","Found 10","Discovery complete"]
```

#### UI checks
1. `/start` → fill inputs → click “Discover Businesses”.  
2. `/discover` shows **live log stream** (EventSource) with 1–2 second intervals.  
3. “Start Scoring” button **appears only after** “Discovery complete”.

---

### Story 2  Discovery with Rate-Limit Backoff
**As** the agent  
**I want** to hit Google Places 429 once, then back-off exponentially  
**So that** we respect ToS.

####   API stub
First request → HTTP 429  
Headers: `Retry-After: 3`  
Second request (after 3 s) → 200 with data.

#### UI checks
- **Toast banner**: “Google throttled us — retrying in 3 s…”  
- **Spinner pauses** for 3 s then continues.  
- **No duplicate rows** are emitted.

---

### Story 3  Scraping Blocked → Yelp Fusion Fallback
**As** the agent  
**I want** to detect robots.txt disallow  
**So that** I immediately switch to Yelp API.

####   API stub
```json
["robots.txt blocks SerpAPI","Switching to Yelp Fusion…","Found 10"]
```

#### UI checks
- Log line shows the switch.  
- Final table length = 10.

---

### Story 4  Scoring with Low-Score Demo Generation
**As** the marketer  
**I want** any site < 70 to get a free demo  
**So that** I have something to pitch.

####   data row
```json
{
  "business_name": "GreenBite ATX",
  "score_overall": 45,
  "score_perf": 10,
  "score_cro": 5,
  "website": "https://greenbite-atx.com"
}
```

#### UI checks
- In `/score` table → row highlighted red.  
- “Generate Demo” link → `/generate?biz=GreenBite%20ATX`.  
- `/generate` page shows **animated “Building site…”** → then **live Vercel URL**.

---

### Story 5  High-Score Skipped Demo
**As** the agent  
**I want** to skip demo generation for ≥ 70 scorers  
**So that** we save build minutes.

####   row
```json
{ "business_name": "VeggieVibes", "score_overall": 86 }
```

#### UI checks
- Table cell shows green check-mark instead of “Generate Demo”.  
- No call to `/api/generate`.

---

### Story 6  CSV / Google Sheet Export
**As** the sales lead  
**I want** all 10 rows + outreach drafts in a Google Sheet  
**So that** I can bulk-import to Woodpecker / WhatsApp sender.

####   API stub (`GET /api/sheet`)
```json
[
  {
    "business_name": "GreenBite ATX",
    "generated_site_url": "https://demo-123.vercel.app",
    "outreach_email": {
      "subject": "Quick win: faster website for GreenBite ATX in Austin",
      "body": "Hi…"
    },
    "outreach_whatsapp": "Hi…",
    "outreach_sms": "Hi…"
  }
]
```

#### UI checks
- `/sheet` loads in < 1 s.  
- “Open in Google Sheets” button opens real sheet in new tab.  
- Copy buttons copy **trimmed 280-char SMS**.

---

### Story 7  Duplicate Run Protection
**As** the operations manager  
**I want** to re-run the same city + niche without duplicates  
**So that** we don’t spam prospects or inflate rows.

#### DB state
Earlier run_id = `2025-08-15-austin-vegan-001`.

#### UI flow
1. Re-enter “Austin, TX” + “Vegan restaurants”.  
2. Agent recognises run_id, shows toast:  
   “Identical run found. Skip, overwrite, or append?”  
3. User chooses **“overwrite”** → new run_id = `2025-08-15-austin-vegan-002`.  
4. Sheet shows **exactly 10 latest rows** (no duplicates).

---

### Bonus Edge-Story  Network Timeout Retry
**As** the agent  
**I want** to retry Lighthouse 3 times on network failure  
**So that** flaky Wi-Fi doesn’t break the demo.

#### Stub sequence
1. `/lighthouse_audit` → `net::ERR_CONNECTION_RESET`.  
2. UI shows **banner**: “Retry 1/3 in 2 s…”.  
3. 2nd → same error.  
4. 3rd → returns score JSON.  
5. Progress bar never goes backwards; banner disappears.

---

### Quick Test Matrix (for Playwright)

```ts
// playwright/smoke.spec.ts
test("Austin vegan E2E", async ({ page }) => {
  await page.goto("/");
  await page.click('button:has-text("Launch Agent")');
  await page.fill('input[placeholder*="City"]', "Austin, TX");
  await page.fill('input[placeholder*="niche"]', "Vegan restaurants");
  await page.click('button:has-text("Discover")');
  await expect(page.locator("text=Discovery complete")).toBeVisible({ timeout: 15000 });
  await expect(page.locator("tr")).toHaveCount(10);
  await page.click('a:has-text("Generate Demo")');
  await expect(page.locator("text=Live preview")).toBeVisible();
});
```

Run with `npx playwright test --headed` to see all animations & retries live.