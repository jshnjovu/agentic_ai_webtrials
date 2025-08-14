from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import csv
from datetime import datetime
import os

app = FastAPI(title="Agentic AI LeadGen Backend")


class BusinessData(BaseModel):
    business_name: str
    niche: str
    location: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    score_overall: Optional[int] = None
    score_perf: Optional[int] = None
    score_access: Optional[int] = None
    score_seo: Optional[int] = None
    score_trust: Optional[int] = None
    score_cro: Optional[int] = None
    top_issues: Optional[List[str]] = None
    generated_site_url: Optional[str] = None
    outreach_email: Optional[str] = None
    outreach_whatsapp: Optional[str] = None
    outreach_sms: Optional[str] = None
    notes: Optional[str] = None


@app.get("/")
def root():
    return {"message": "Agentic AI LeadGen API running"}


@app.post("/save_results")
def save_results(data: List[BusinessData]):
    os.makedirs("../data", exist_ok=True)
    filename = f"../data/output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fieldnames = list(BusinessData.model_fields.keys())
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row.model_dump())
    return {"status": "success", "file": filename}
