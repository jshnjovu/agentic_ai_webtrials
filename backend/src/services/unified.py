"""
Unified Website Analyzer (Python back-port of unified.js)
"""

import logging
import math
import asyncio
from typing import Dict, Any, List
from urllib.parse import urlparse

import requests

from .domain_analysis import DomainAnalysisService
from ..core.config import get_api_config

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("unified")


class UnifiedAnalyzer:
    def __init__(self) -> None:
        self.pagespeed_base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.api_config = get_api_config()
        self.google_api_key = self.api_config.GOOGLE_GENERAL_API_KEY

        try:
            self.domain_service = DomainAnalysisService()
        except Exception as e:
            log.warning("⚠️ Domain Analysis Service not available: %s", e)
            self.domain_service = None

    # ------------------------------------------------------------------ #
    async def make_request(self, url: str, **kwargs) -> Dict[str, Any]:
        try:
            resp = requests.get(url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            raise RuntimeError(
                f"Request failed with status {e.response.status_code}: {e.response.reason}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}") from e

    # ------------------------------------------------------------------ #
    def extract_metric(self, metric: Dict[str, Any]) -> Dict[str, Any] | None:
        if not metric:
            return None
        return {
            "value": metric["numericValue"],
            "displayValue": metric["displayValue"],
            "unit": metric.get("numericUnit", ""),
        }

    # ------------------------------------------------------------------ #
    def extract_opportunities(self, audits: Dict[str, Any]) -> List[Dict[str, Any]]:
        opportunities = []
        for key, audit in audits.items():
            if audit.get("details", {}).get("type") == "opportunity" and audit.get(
                "numericValue", 0
            ) > 0:
                opportunities.append(
                    {
                        "title": audit["title"],
                        "description": audit["description"],
                        "potentialSavings": round(audit["numericValue"]),
                        "unit": audit.get("numericUnit", "ms"),
                    }
                )
        return opportunities[:3]

    # ------------------------------------------------------------------ #
    async def run_page_speed_analysis(
        self, url: str, strategy: str = "mobile"
    ) -> Dict[str, Any]:
        categories = ["performance", "accessibility", "best-practices", "seo"]
        category_params = "&".join([f"category={c}" for c in categories])
        api_url = (
            f"{self.pagespeed_base_url}?url={url}&strategy={strategy}"
            f"&{category_params}&prettyPrint=true&key={self.google_api_key}"
        )

        data = await self.make_request(api_url)

        if data.get("error"):
            raise RuntimeError(data["error"]["message"])

        lighthouse = data.get("lighthouseResult", {})
        scores = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})

        return {
            "scores": {
                "performance": round((scores["performance"]["score"] or 0) * 100),
                "accessibility": round((scores["accessibility"]["score"] or 0) * 100),
                "bestPractices": round((scores["best-practices"]["score"] or 0) * 100),
                "seo": round((scores["seo"]["score"] or 0) * 100),
            },
            "coreWebVitals": {
                "largestContentfulPaint": self.extract_metric(
                    audits.get("largest-contentful-paint")
                ),
                "firstInputDelay": self.extract_metric(
                    audits.get("max-potential-fid") or audits.get("first-input-delay")
                ),
                "cumulativeLayoutShift": self.extract_metric(
                    audits.get("cumulative-layout-shift")
                ),
                "firstContentfulPaint": self.extract_metric(
                    audits.get("first-contentful-paint")
                ),
                "speedIndex": self.extract_metric(audits.get("speed-index")),
            },
            "serverMetrics": {
                "serverResponseTime": self.extract_metric(
                    audits.get("server-response-time")
                ),
                "totalBlockingTime": self.extract_metric(
                    audits.get("total-blocking-time")
                ),
                "timeToInteractive": self.extract_metric(audits.get("interactive")),
            },
            "mobileUsability": self.analyze_mobile_usability_from_pagespeed(audits),
            "opportunities": self.extract_opportunities(audits),
        }

    # ------------------------------------------------------------------ #
    def analyze_mobile_usability_from_pagespeed(
        self, audits: Dict[str, Any]
    ) -> Dict[str, Any]:
        checks = {
            "hasViewportMetaTag": (audits.get("viewport") or {}).get("score") == 1,
            "contentSizedCorrectly": (audits.get("content-width") or {}).get("score")
            == 1,
            "tapTargetsAppropriateSize": (audits.get("tap-targets") or {}).get("score")
            == 1,
            "textReadable": (audits.get("font-size") or {}).get("score") == 1,
            "isResponsive": True,
        }

        passed = sum(bool(v) for v in checks.values())
        mobile_score = round((passed / len(checks)) * 100)

        return {
            "mobileFriendly": mobile_score >= 80,
            "score": mobile_score,
            "checks": checks,
            "issues": self.get_mobile_issues(checks),
            "realData": True,
        }

    # ------------------------------------------------------------------ #
    def get_mobile_issues(self, checks: Dict[str, bool]) -> List[str]:
        issues = []
        if not checks["hasViewportMetaTag"]:
            issues.append("Missing viewport meta tag")
        if not checks["contentSizedCorrectly"]:
            issues.append("Content not sized correctly for viewport")
        if not checks["tapTargetsAppropriateSize"]:
            issues.append("Tap targets too small")
        if not checks["textReadable"]:
            issues.append("Text too small to read")
        return issues

    # ------------------------------------------------------------------ #
    async def analyze_trust(self, url: str) -> Dict[str, Any]:
        try:
            domain = urlparse(url).hostname
            trust = {
                "ssl": False,
                "securityHeaders": [],
                "domainAge": "unknown",
                "score": 0,
                "realData": {"ssl": True, "securityHeaders": True, "domainAge": False},
                "warnings": [],
            }

            # SSL
            try:
                ssl_resp = requests.get(
                    f"https://{domain}", timeout=10, allow_redirects=True
                )
                trust["ssl"] = ssl_resp.status_code < 400
                trust["score"] += 30 if trust["ssl"] else 0
            except Exception as e:
                trust["warnings"].append(f"SSL check failed: {e}")

            # Security headers
            try:
                hdr_resp = requests.get(
                    f"https://{domain}", timeout=10, allow_redirects=True
                )
                headers = {k.lower(): v for k, v in hdr_resp.headers.items()}

                sec_headers = [
                    "x-frame-options",
                    "x-content-type-options",
                    "strict-transport-security",
                    "content-security-policy",
                    "x-xss-protection",
                ]
                trust["securityHeaders"] = [h for h in sec_headers if h in headers]
                trust["score"] += min(40, len(trust["securityHeaders"]) * 8)
            except Exception as e:
                trust["warnings"].append(f"Security headers check failed: {e}")

            # Domain age
            if self.domain_service:
                try:
                    analysis = await self.domain_service.analyze_domain(domain)
                    age = analysis["domainAge"]
                    trust["domainAge"] = (
                        f"{age['years']} years, {age['months']} months, {age['days']} days"
                    )
                    trust["realData"]["domainAge"] = True

                    if age["years"] >= 10:
                        trust["score"] += 15
                    elif age["years"] >= 5:
                        trust["score"] += 12
                    elif age["years"] >= 2:
                        trust["score"] += 8
                    elif age["years"] >= 1:
                        trust["score"] += 5
                    else:
                        trust["score"] += 2

                except Exception as e:
                    trust["warnings"].append(f"Domain age analysis failed: {e}")
                    trust["domainAge"] = self.estimate_domain_age(domain)
                    trust["realData"]["domainAge"] = False
                    trust["score"] += 3
            else:
                trust["domainAge"] = self.estimate_domain_age(domain)
                trust["realData"]["domainAge"] = False
                trust["score"] += 3
                trust["warnings"].append("Domain age estimation only - service not available")

            return trust

        except Exception as e:
            raise RuntimeError(f"Trust analysis error: {e}") from e

    # ------------------------------------------------------------------ #
    def estimate_domain_age(self, domain: str) -> str:
        if len(domain) <= 8 and "-" not in domain and "2" not in domain:
            return "5+ years (estimated)"
        if any(year in domain for year in ["2020", "2021", "2022"]):
            return "2-3 years (estimated)"
        if "new" in domain or "latest" in domain:
            return "1-2 years (estimated)"
        return "3-5 years (estimated)"

    # ------------------------------------------------------------------ #
    async def analyze_cro(self, url: str) -> Dict[str, Any]:
        try:
            mobile_data = await self.run_page_speed_analysis(url, "mobile")
            desktop_data = await self.run_page_speed_analysis(url, "desktop")

            cro = {
                "mobileFriendly": mobile_data["mobileUsability"]["mobileFriendly"],
                "mobileUsabilityScore": mobile_data["mobileUsability"]["score"],
                "mobileIssues": mobile_data["mobileUsability"]["issues"],
                "pageSpeed": {
                    "mobile": mobile_data["scores"]["performance"],
                    "desktop": desktop_data["scores"]["performance"],
                    "average": round(
                        (
                            mobile_data["scores"]["performance"]
                            + desktop_data["scores"]["performance"]
                        )
                        / 2
                    ),
                },
                "userExperience": {
                    "loadingTime": self.calculate_ux_score(mobile_data["coreWebVitals"]),
                    "interactivity": self.calculate_interactivity_score(
                        mobile_data["serverMetrics"]
                    ),
                    "visualStability": self.calculate_visual_stability_score(
                        mobile_data["coreWebVitals"]
                    ),
                },
                "score": 0,
                "realData": True,
            }

            cro["score"] = round(
                cro["mobileUsabilityScore"] * 0.3
                + cro["pageSpeed"]["average"] * 0.4
                + cro["userExperience"]["loadingTime"] * 0.3
            )

            return cro

        except Exception as e:
            raise RuntimeError(f"CRO analysis error: {e}") from e

    # ------------------------------------------------------------------ #
    def calculate_ux_score(self, cwv: Dict[str, Any]) -> int:
        score = 100
        lcp = (cwv.get("largestContentfulPaint") or {}).get("value") or 0
        if lcp > 4000:
            score -= 30
        elif lcp > 2500:
            score -= 15

        cls = (cwv.get("cumulativeLayoutShift") or {}).get("value") or 0
        if cls > 0.25:
            score -= 25
        elif cls > 0.1:
            score -= 10

        return max(0, score)

    # ------------------------------------------------------------------ #
    def calculate_interactivity_score(self, sm: Dict[str, Any]) -> int:
        score = 100
        tti = (sm.get("timeToInteractive") or {}).get("value") or 0
        if tti > 5000:
            score -= 30
        elif tti > 3000:
            score -= 15

        tbt = (sm.get("totalBlockingTime") or {}).get("value") or 0
        if tbt > 600:
            score -= 25
        elif tbt > 300:
            score -= 10

        return max(0, score)

    # ------------------------------------------------------------------ #
    def calculate_visual_stability_score(self, cwv: Dict[str, Any]) -> int:
        cls = (cwv.get("cumulativeLayoutShift") or {}).get("value") or 0
        if cls <= 0.1:
            return 100
        if cls <= 0.25:
            return 80
        return 50

    # ------------------------------------------------------------------ #
    async def analyze_uptime(self, url: str) -> Dict[str, Any]:
        try:
            results = []
            for i in range(3):
                start = asyncio.get_event_loop().time()
                try:
                    requests.get(url, timeout=10)
                    elapsed = int((asyncio.get_event_loop().time() - start) * 1000)
                    results.append({"success": True, "responseTime": elapsed})
                except Exception:
                    results.append({"success": False, "responseTime": 10_000})

                if i < 2:
                    await asyncio.sleep(1)

            success_count = sum(r["success"] for r in results)
            avg_time = sum(r["responseTime"] for r in results) / len(results)
            uptime = (success_count / len(results)) * 100

            score = 100
            if uptime < 100:
                score -= (100 - uptime) * 2
            if avg_time > 3000:
                score -= 20
            elif avg_time > 1000:
                score -= 10

            return {
                "score": max(0, round(score)),
                "uptime": f"{uptime:.1f}%",
                "averageResponseTime": round(avg_time),
                "status": "up" if uptime > 66 else "down",
                "realData": True,
            }

        except Exception as e:
            raise RuntimeError(f"Uptime analysis error: {e}") from e