"""
Domain History and Age Analysis Service
Integrates WHOIS and DNS History APIs from WHOISXMLAPIs
"""

import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

import requests
from ..core.config import get_api_config

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("domain-analysis")


class DomainAnalysisService:
    def __init__(self) -> None:
        self.api_config = get_api_config()
        self.whois_api_key = self.api_config.WHOIS_API_KEY
        self.whois_base_url = self.api_config.WHOIS_API_BASE_URL
        self.whois_history_base_url = self.api_config.WHOIS_HISTORY_API_BASE_URL

        if not self.whois_api_key:
            raise RuntimeError("WHOIS_API_KEY is required in environment configuration")

    # ------------------------------------------------------------------ #
    async def analyze_domain(self, domain: str) -> Dict[str, Any]:
        try:
            log.info("🔍 Analyzing domain: %s", domain)

            whois_data = await self.get_whois_info(domain)
            whois_history = await self.get_whois_history(domain)

            log.info("\n📊 RAW WHOIS DATA:")
            log.info("%s", _pretty(whois_data))

            log.info("\n📊 RAW WHOIS HISTORY DATA:")
            log.info("%s", _pretty(whois_history))

            domain_age = self.calculate_domain_age(whois_data["createdDate"])

            analysis = {
                "domain": domain,
                "whois": whois_data,
                "whoisHistory": whois_history,
                "domainAge": domain_age,
                "analysis": {
                    "isEstablished": domain_age["years"] >= 2,
                    "isVeteran": domain_age["years"] >= 5,
                    "credibility": self.calculate_credibility_score(
                        whois_data, whois_history, domain_age
                    ),
                },
            }

            log.info("✅ Analysis complete for %s", domain)
            return analysis

        except Exception as e:
            log.error("❌ Error analyzing domain %s: %s", domain, e)
            raise

    # ------------------------------------------------------------------ #
    async def get_whois_info(self, domain: str) -> Dict[str, Any]:
        url = f"{self.whois_base_url}/whoisserver/WhoisService"
        params = {
            "domainName": domain,
            "outputFormat": "JSON",
            "_hardRefresh": 1,
            "apiKey": self.whois_api_key,
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            log.info("\n🔍 RAW WHOIS API RESPONSE:")
            log.info("%s", _pretty(data))

            whois = data.get("WhoisRecord", {})
            if not whois:
                raise ValueError("Invalid WHOIS response format")

            created_date = whois.get("createdDate")
            updated_date = whois.get("updatedDate")
            expires_date = whois.get("expiresDate")
            registrar = whois.get("registrarName")
            status = whois.get("status")
            name_servers = (whois.get("nameServers") or {}).get("hostNames", [])

            # Fallback to registryData
            registry = whois.get("registryData", {})
            if not created_date and registry:
                created_date = registry.get("createdDate")
                updated_date = registry.get("updatedDate")
                expires_date = registry.get("expiresDate")
                registrar = registry.get("registrarName") or registrar
                status = registry.get("status") or status
                name_servers = (
                    (registry.get("nameServers") or {}).get("hostNames") or name_servers
                )

            return {
                "createdDate": created_date,
                "updatedDate": updated_date,
                "expiresDate": expires_date,
                "registrar": registrar,
                "status": status,
                "ips": self.extract_ips(whois),
                "nameServers": name_servers,
                "registrant": (whois.get("registrant") or {}).get("organization") or "Unknown",
                "country": (whois.get("registrant") or {}).get("countryCode") or "Unknown",
            }

        except Exception as e:
            raise RuntimeError(f"WHOIS lookup failed: {e}") from e

    # ------------------------------------------------------------------ #
    async def get_whois_history(self, domain: str) -> Optional[Dict[str, Any]]:
        url = f"{self.whois_history_base_url}/api/v1"
        params = {"domainName": domain, "outputFormat": "JSON", "apiKey": self.whois_api_key}

        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            log.info("\n🔍 RAW WHOIS HISTORY API RESPONSE:")
            log.info("%s", _pretty(data))

            if data.get("recordsCount") is not None:
                return {
                    "totalRecords": data["recordsCount"],
                    "firstSeen": None,
                    "lastVisit": None,
                    "records": [],
                    "note": "API returns only count, not individual records",
                }
            return None

        except Exception as e:
            log.warning("WHOIS History lookup failed for domain %s: %s", domain, e)
            return None

    # ------------------------------------------------------------------ #
    def calculate_domain_age(self, created_date: Optional[str]) -> Dict[str, Any]:
        if not created_date:
            return {
                "years": 0,
                "months": 0,
                "days": 0,
                "totalDays": 0,
                "createdDate": None,
                "ageDescription": "Unknown",
            }

        try:
            created = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
        except Exception:
            return {
                "years": 0,
                "months": 0,
                "days": 0,
                "totalDays": 0,
                "createdDate": None,
                "ageDescription": "Invalid Date",
            }

        delta = datetime.now(timezone.utc) - created
        total_days = delta.days
        years, rem = divmod(total_days, 365)
        months = math.floor(rem / 30)
        days = rem % 30

        return {
            "years": years,
            "months": months,
            "days": days,
            "totalDays": total_days,
            "createdDate": created.isoformat(),
            "ageDescription": self.get_age_description(years, months),
        }

    # ------------------------------------------------------------------ #
    def get_age_description(self, years: int, months: int) -> str:
        if years >= 10:
            return "Veteran"
        if years >= 5:
            return "Established"
        if years >= 2:
            return "Mature"
        if years >= 1:
            return "Young"
        if months >= 6:
            return "Recent"
        if months >= 1:
            return "New"
        return "Very New"

    # ------------------------------------------------------------------ #
    def calculate_credibility_score(
        self, whois_data: Dict[str, Any], whois_history: Dict[str, Any], domain_age: Dict[str, Any]
    ) -> int:
        score = 0

        # Domain age
        if domain_age["years"] >= 5:
            score += 40
        elif domain_age["years"] >= 2:
            score += 30
        elif domain_age["years"] >= 1:
            score += 20
        elif domain_age["months"] >= 6:
            score += 10

        # Registration status
        status = whois_data.get("status") or ""
        if status and "expired" not in str(status).lower():
            score += 20

        # Name servers
        if len(whois_data.get("nameServers") or []) >= 2:
            score += 15

        # WHOIS history
        total_records = whois_history.get("totalRecords", 0) if whois_history else 0
        score += min(15, total_records // 10)

        # Registrar reputation
        registrar = whois_data.get("registrar") or ""
        if registrar and "Unknown" not in registrar:
            score += 10

        return min(100, score)

    # ------------------------------------------------------------------ #
    def extract_ips(self, whois: Dict[str, Any]) -> List[str]:
        ips = []

        # nameServers.ips
        ns = whois.get("nameServers") or {}
        ips.extend(ns.get("ips") or [])

        registry = whois.get("registryData", {})
        reg_ns = registry.get("nameServers") or {}
        ips.extend(reg_ns.get("ips") or [])

        return ips


# ---------------------------------------------------------------------- #
# Helper
def _pretty(obj: Any) -> str:
    import json

    return json.dumps(obj, indent=2, ensure_ascii=False)