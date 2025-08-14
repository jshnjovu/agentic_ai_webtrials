"""
Content generation API endpoints for demo site creation.
"""

from fastapi import APIRouter, HTTPException, Depends
import uuid
from src.schemas.content_generation import (
	ContentGenerationRequest,
	ContentGenerationResponse,
	ContentGenerationError
)
from src.services.content_generation_service import ContentGenerationService

router = APIRouter(prefix="/content-generation", tags=["content-generation"])


def get_content_generation_service() -> ContentGenerationService:
	"""Dependency to get ContentGenerationService instance."""
	return ContentGenerationService()


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
	request: ContentGenerationRequest,
	service: ContentGenerationService = Depends(get_content_generation_service)
) -> ContentGenerationResponse:
	"""
	Generate business-specific content for demo sites using heuristics or AI.
	"""
	try:
		if not request.run_id:
			request.run_id = str(uuid.uuid4())

		if not service.validate_input(request):
			raise HTTPException(status_code=400, detail="Invalid content generation request")

		result = service.generate_content(request)

		if isinstance(result, ContentGenerationError) or not getattr(result, 'success', False):
			raise HTTPException(
				status_code=400,
				detail={
					"error": getattr(result, 'error', 'Generation failed'),
					"error_code": getattr(result, 'error_code', 'GENERATION_FAILED'),
					"context": getattr(result, 'context_info', 'content_generation'),
					"run_id": request.run_id
				}
			)

		return result
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Internal server error during content generation: {str(e)}")