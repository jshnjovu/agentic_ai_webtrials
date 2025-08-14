"""
Service for AI-powered content generation for demo sites.
Uses heuristic templates by default, with optional LLM support if configured.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from src.core.base_service import BaseService
from src.core.config import get_api_config
from src.schemas.content_generation import (
	ContentGenerationRequest,
	ContentGenerationResponse,
	ContentGenerationError,
	BusinessContext,
	ContentTone,
	ServiceItem,
	SiteContent,
	SEOData
)

# Optional OpenAI import guarded for environments without the dependency
try:
	from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - environment without openai
	OpenAI = None  # type: ignore


class ContentGenerationService(BaseService):
	"""Generates structured website content for a business context."""

	def __init__(self):
		super().__init__(service_name="ContentGenerationService")
		self.api_config = get_api_config()

	def validate_input(self, data: Any) -> bool:
		"""Validate input request object."""
		try:
			request: ContentGenerationRequest = data if isinstance(data, ContentGenerationRequest) else ContentGenerationRequest(**data)
			# Basic required fields are validated by pydantic; additional checks here
			return len(request.context.name.strip()) > 0 and len(request.context.niche.strip()) > 0 and len(request.context.city.strip()) > 0
		except Exception:
			return False

	def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse | ContentGenerationError:
		"""Generate content using heuristics or LLM based on configuration and request flag."""
		try:
			self.log_operation(
				operation="content_generation_start",
				run_id=request.run_id,
				business_id=request.context.business_id,
				niche=request.context.niche,
				city=request.context.city,
				tone=request.tone.value,
				use_ai=str(request.use_ai)
			)

			# Prefer heuristic generation; only use LLM if explicitly requested and configured
			use_llm = bool(request.use_ai and getattr(self.api_config, 'OPENAI_API_KEY', None) and OpenAI is not None)
			if use_llm:
				try:
					return self._generate_with_llm(request)
				except Exception as openai_error:
					# Fall back to heuristic generation on failure
					self.log_error(openai_error, operation="content_generation_llm_failed", run_id=request.run_id)
					return self._generate_with_heuristics(request, model_used=None)
			else:
				return self._generate_with_heuristics(request, model_used=None)
		except Exception as e:
			return ContentGenerationError(
				error=str(e),
				error_code="GENERATION_FAILED",
				context_info="content_generation",
				run_id=request.run_id
			)

	def _generate_with_heuristics(self, request: ContentGenerationRequest, model_used: Optional[str]) -> ContentGenerationResponse:
		"""Deterministic template-based generation that requires no external API."""
		context = request.context
		services = self._determine_services(context.niche, request.requested_services)
		seo_keywords = self._compose_keywords(context, request, services)
		hero = self._compose_hero(context, request.tone)
		about = self._compose_about(context, request.tone)
		contact_section = self._compose_contact_section(context)
		seo_data = self._compose_seo(context, seo_keywords, request)

		content = SiteContent(
			hero=hero,
			services=services,
			about=about,
			contact_section=contact_section
		)

		return ContentGenerationResponse(
			success=True,
			context=context,
			tone=request.tone,
			content=content,
			seo=seo_data,
			model_used=model_used,
			run_id=request.run_id
		)

	def _generate_with_llm(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
		"""Use OpenAI to generate content. Falls back to heuristics if anything fails."""
		# Safety: ensure OpenAI client is available and configured
		api_key = getattr(self.api_config, 'OPENAI_API_KEY', None)
		if not api_key or OpenAI is None:
			return self._generate_with_heuristics(request, model_used=None)

		client = OpenAI(api_key=api_key)
		model_name = getattr(self.api_config, 'OPENAI_MODEL', 'gpt-4o-mini')

		# Construct a concise system and user prompt based on the request
		prompt = self._build_llm_prompt(request)

		try:
			# Use responses.create (chat/completions depends on SDK version)
			completion = client.responses.create(
				model=model_name,
				input=prompt,
			)
			text = completion.output_text  # type: ignore[attr-defined]
			# Attempt to parse as JSON-like; fallback to heuristics if parsing fails
			parsed = self._try_parse_generated_json(text)
			if not parsed:
				return self._generate_with_heuristics(request, model_used=model_name)

			# Map parsed to schema objects
			services = [
				ServiceItem(title=s.get('title', 'Service'), description=s.get('description', ''), icon=s.get('icon', 'star'))
				for s in parsed.get('services', [])
			]
			hero = parsed.get('hero', {})
			about = parsed.get('about', '')
			contact_section = parsed.get('contact_section', {})
			seo = parsed.get('seo', {})

			content = SiteContent(hero=hero, services=services, about=about, contact_section=contact_section)
			seo_data = SEOData(
				meta_title=seo.get('meta_title', self._default_meta_title(request.context)),
				meta_description=seo.get('meta_description', self._default_meta_description(request.context)),
				keywords=seo.get('keywords', self._compose_keywords(request.context, request, services)),
				schema_markup=seo.get('schema_markup', self._build_schema_markup(request.context, services))
			)

			return ContentGenerationResponse(
				success=True,
				context=request.context,
				tone=request.tone,
				content=content,
				seo=seo_data,
				model_used=model_name,
				run_id=request.run_id
			)
		except Exception:
			# On any failure, use heuristics
			return self._generate_with_heuristics(request, model_used=None)

	def _determine_services(self, niche: str, requested: Optional[List[str]]) -> List[ServiceItem]:
		"""Return a services list based on niche or requested items."""
		if requested:
			return [ServiceItem(title=title, description=self._service_description(niche, title), icon=self._icon_for_service(title)) for title in requested]

		catalog: Dict[str, List[str]] = {
			"plumber": ["Emergency Repairs", "Leak Detection", "Drain Cleaning"],
			"dentist": ["Checkups & Cleaning", "Cosmetic Dentistry", "Dental Implants"],
			"restaurant": ["Online Ordering", "Catering", "Private Events"],
			"lawyer": ["Consultations", "Contract Review", "Dispute Resolution"],
			"salon": ["Haircuts & Styling", "Coloring", "Treatments"],
		}
		default_services = ["Our Services", "Consultations", "Support"]
		titles = catalog.get(niche.lower(), default_services)
		return [ServiceItem(title=t, description=self._service_description(niche, t), icon=self._icon_for_service(t)) for t in titles]

	def _compose_hero(self, context: BusinessContext, tone: ContentTone) -> Dict[str, str]:
		"""Build hero section with local SEO."""
		headline = f"{context.niche.title()} in {context.city}{', ' + context.region if context.region else ''}"
		subheadline = self._tone_wrap(
			f"Trusted {context.niche.lower()} services for {context.city} and nearby communities.", tone
		)
		cta = self._tone_cta(tone)
		return {"headline": headline, "subheadline": subheadline, "cta_text": cta}

	def _compose_about(self, context: BusinessContext, tone: ContentTone) -> str:
		"""Build about content tailored to tone and niche."""
		base = (
			f"{context.name} is a {context.niche.lower()} serving {context.city}"
			+ (f", {context.region}" if context.region else "")
			+ (f", {context.country}" if context.country else "")
			+ ". We combine quality craftsmanship with dependable service to meet your needs."
		)
		return self._tone_wrap(base, tone)

	def _compose_contact_section(self, context: BusinessContext) -> Dict[str, Any]:
		"""Integrate contact info and build simple form fields and map embed placeholder."""
		form_fields = ["name", "email", "phone", "message"]
		map_embed = f"https://www.google.com/maps?q={context.city.replace(' ', '+')}" if context.city else ""
		contact = context.contact.dict() if context.contact else {}
		return {"form_fields": form_fields, "map_embed": map_embed, "contact": contact}

	def _compose_seo(self, context: BusinessContext, keywords: List[str], request: ContentGenerationRequest) -> SEOData:
		"""Compose SEO metadata including optional schema markup."""
		meta_title = self._default_meta_title(context)
		meta_description = self._default_meta_description(context)
		schema = self._build_schema_markup(context, self._determine_services(context.niche, request.requested_services)) if (request.seo and request.seo.include_schema_markup) else None
		return SEOData(meta_title=meta_title, meta_description=meta_description, keywords=keywords, schema_markup=schema)

	def _default_meta_title(self, context: BusinessContext) -> str:
		return f"{context.niche.title()} | {context.name} | {context.city}{', ' + context.region if context.region else ''}"

	def _default_meta_description(self, context: BusinessContext) -> str:
		return f"{context.name} offers {context.niche.lower()} services in {context.city}. Call today for reliable help."

	def _build_schema_markup(self, context: BusinessContext, services: List[ServiceItem]) -> Dict[str, Any]:
		"""Build LocalBusiness JSON-LD schema."""
		contact = context.contact
		service_offers = [{
			"@type": "Offer",
			"itemOffered": {"@type": "Service", "name": s.title, "description": s.description}
		} for s in services]

		schema: Dict[str, Any] = {
			"@context": "https://schema.org",
			"@type": "LocalBusiness",
			"name": context.name,
			"address": {
				"@type": "PostalAddress",
				"addressLocality": context.city,
				"addressRegion": context.region,
				"postalCode": contact.postal_code if contact and contact.postal_code else None,
				"addressCountry": context.country
			},
			"telephone": contact.phone if contact and contact.phone else None,
			"email": contact.email if contact and contact.email else None,
			"url": str(context.website_url) if context.website_url else None,
			"areaServed": context.city,
			"makesOffer": service_offers
		}
		# Remove None values recursively for cleanliness
		return self._prune_nones(schema)

	def _compose_keywords(self, context: BusinessContext, request: ContentGenerationRequest, services: List[ServiceItem]) -> List[str]:
		base = [
			f"{context.city} {context.niche}",
			f"{context.niche} near me",
			f"best {context.niche} in {context.city}"
		]
		if context.region:
			base.append(f"{context.niche} in {context.city} {context.region}")
		if request.seo and request.seo.primary_keyword:
			base.append(request.seo.primary_keyword)
		if request.seo and request.seo.secondary_keywords:
			base.extend(request.seo.secondary_keywords)
		# Add service-specific keywords
		for s in services:
			base.append(f"{s.title} {context.niche} {context.city}")
		# Deduplicate while preserving order
		seen = set()
		keywords: List[str] = []
		for k in base:
			if k not in seen:
				seen.add(k)
				keywords.append(k)
		return keywords

	def _service_description(self, niche: str, service_title: str) -> str:
		return f"Professional {service_title.lower()} by experienced {niche.lower()} specialists."

	def _icon_for_service(self, title: str) -> str:
		key = title.lower()
		if "repair" in key or "clean" in key:
			return "wrench"
		if "consult" in key:
			return "chat"
		if "order" in key or "catering" in key:
			return "bag"
		return "star"

	def _tone_wrap(self, text: str, tone: ContentTone) -> str:
		prefix_map = {
			ContentTone.PROFESSIONAL: "",
			ContentTone.FRIENDLY: "Friendly: ",
			ContentTone.ENERGETIC: "Fast, reliable: ",
			ContentTone.CALM: "Thoughtful & caring: ",
			ContentTone.LUXURY: "Premium quality: ",
			ContentTone.BUDGET: "Affordable: ",
		}
		prefix = prefix_map.get(tone, "")
		return (prefix + text).strip()

	def _tone_cta(self, tone: ContentTone) -> str:
		cta_map = {
			ContentTone.PROFESSIONAL: "Request a Quote",
			ContentTone.FRIENDLY: "Talk to Us",
			ContentTone.ENERGETIC: "Call Now",
			ContentTone.CALM: "Get in Touch",
			ContentTone.LUXURY: "Book a Consultation",
			ContentTone.BUDGET: "Get a Free Estimate",
		}
		return cta_map.get(tone, "Contact Us")

	def _prune_nones(self, obj: Any) -> Any:
		if isinstance(obj, dict):
			return {k: self._prune_nones(v) for k, v in obj.items() if v is not None}
		if isinstance(obj, list):
			return [self._prune_nones(v) for v in obj if v is not None]
		return obj

	def _build_llm_prompt(self, request: ContentGenerationRequest) -> str:
		ctx = request.context
		region_part = f", {ctx.region}" if ctx.region else ""
		country_part = f", {ctx.country}" if ctx.country else ""
		kw = ", ".join(ctx.keywords or [])
		audience = f"Target audience: {request.target_audience}." if request.target_audience else ""
		return (
			f"Generate JSON for website content with keys hero, services[], about, contact_section, seo. "
			f"Business: name='{ctx.name}', niche='{ctx.niche}', city='{ctx.city}'{region_part}{country_part}. "
			f"Tone='{request.tone.value}'. {audience} Keywords: {kw}. "
			"Keep text concise, local SEO friendly, and return pure JSON only."
		)

	def _try_parse_generated_json(self, text: str) -> Optional[Dict[str, Any]]:
		import json
		try:
			return json.loads(text)
		except Exception:
			return None