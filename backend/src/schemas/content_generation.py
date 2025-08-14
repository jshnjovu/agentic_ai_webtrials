"""
Schemas for AI-powered content generation for demo sites.
"""

from pydantic import BaseModel, Field, AnyUrl, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class ContentTone(str, Enum):
	"""Supported tones for generated content."""
	PROFESSIONAL = "professional"
	FRIENDLY = "friendly"
	ENERGETIC = "energetic"
	CALM = "calm"
	LUXURY = "luxury"
	BUDGET = "budget"


class ContactDetails(BaseModel):
	"""Contact information to integrate into generated content."""
	phone: Optional[str] = Field(None, description="Business phone number")
	email: Optional[str] = Field(None, description="Business contact email")
	website: Optional[AnyUrl] = Field(None, description="Business website URL")
	address_line1: Optional[str] = Field(None, description="Street address line 1")
	address_line2: Optional[str] = Field(None, description="Street address line 2")
	city: Optional[str] = Field(None, description="City")
	region: Optional[str] = Field(None, description="State/Region/Province")
	postal_code: Optional[str] = Field(None, description="Postal/ZIP code")
	country: Optional[str] = Field(None, description="Country")


class BusinessContext(BaseModel):
	"""Core business context used for content generation."""
	business_id: Optional[str] = Field(None, description="Unique identifier for the business")
	name: str = Field(..., description="Business name", min_length=1, max_length=120)
	niche: str = Field(..., description="Business niche/category (e.g. 'plumber', 'dentist')", min_length=1, max_length=120)
	city: str = Field(..., description="City or locality", min_length=1, max_length=120)
	region: Optional[str] = Field(None, description="State/Region/Province")
	country: Optional[str] = Field(None, description="Country")
	keywords: List[str] = Field(default_factory=list, description="Optional additional SEO keywords")
	contact: Optional[ContactDetails] = Field(None, description="Contact details to include")
	website_url: Optional[AnyUrl] = Field(None, description="Existing website URL, if any")


class SEOConfiguration(BaseModel):
	"""Optional SEO configuration for content generation."""
	include_schema_markup: bool = Field(default=True, description="Whether to include JSON-LD schema markup")
	primary_keyword: Optional[str] = Field(None, description="Primary SEO keyword")
	secondary_keywords: List[str] = Field(default_factory=list, description="Additional SEO keywords")


class ContentGenerationRequest(BaseModel):
	"""Request model for demo site content generation."""
	context: BusinessContext = Field(..., description="Business context for generation")
	tone: ContentTone = Field(default=ContentTone.PROFESSIONAL, description="Desired content tone")
	target_audience: Optional[str] = Field(None, description="Brief description of target audience")
	requested_services: Optional[List[str]] = Field(None, description="Optional explicit list of services to emphasize")
	seo: Optional[SEOConfiguration] = Field(default_factory=SEOConfiguration, description="SEO configuration")
	use_ai: bool = Field(default=False, description="If true and API key available, use LLM for generation; otherwise heuristic templates")
	run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")

	@validator('requested_services')
	@classmethod
	def validate_requested_services(cls, v):
		if v is not None and len(v) == 0:
			raise ValueError('requested_services, if provided, must contain at least one item')
		return v


class ServiceItem(BaseModel):
	"""A single service entry for the Services section."""
	title: str = Field(..., min_length=2, max_length=120)
	description: str = Field(..., min_length=10, max_length=800)
	icon: str = Field(default="star", description="Icon name or identifier")


class SiteContent(BaseModel):
	"""Structured content for the generated site."""
	hero: Dict[str, str] = Field(..., description="Hero section content with headline, subheadline, cta_text")
	services: List[ServiceItem] = Field(..., description="List of service entries")
	about: str = Field(..., description="About section content")
	contact_section: Dict[str, Any] = Field(..., description="Contact section data including form fields and map embed if any")


class SEOData(BaseModel):
	"""SEO metadata and schema for the site."""
	meta_title: str = Field(..., min_length=10, max_length=120)
	meta_description: str = Field(..., min_length=30, max_length=160)
	keywords: List[str] = Field(default_factory=list)
	schema_markup: Optional[Dict[str, Any]] = Field(None, description="JSON-LD schema.org markup for LocalBusiness")


class ContentGenerationResponse(BaseModel):
	"""Response for content generation."""
	success: bool = Field(..., description="Whether generation was successful")
	context: BusinessContext = Field(..., description="Echo of input context")
	tone: ContentTone = Field(..., description="Tone actually used")
	content: SiteContent = Field(..., description="Generated site content")
	seo: SEOData = Field(..., description="SEO metadata and schema")
	model_used: Optional[str] = Field(None, description="LLM model used if any")
	prompt_tokens: Optional[int] = Field(None, description="Estimated prompt tokens if LLM used")
	completion_tokens: Optional[int] = Field(None, description="Estimated completion tokens if LLM used")
	total_tokens: Optional[int] = Field(None, description="Estimated total tokens if LLM used")
	run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")


class ContentGenerationError(BaseModel):
	"""Error model for content generation failures."""
	success: bool = Field(default=False, description="Generation was not successful")
	error: str = Field(..., description="Error message")
	error_code: Optional[str] = Field(None, description="Specific error code if available")
	context_info: Optional[str] = Field(None, description="Context where the error occurred")
	run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")
	details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")