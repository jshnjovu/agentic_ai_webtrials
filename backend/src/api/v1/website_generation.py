"""
Website Generation API
Handles website generation for low-scoring businesses
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any, List
import logging
from pathlib import Path
import os

from src.services.website_template_service import WebsiteTemplateService
from src.schemas.website_scoring import WebsiteScoringResponse
from src.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/website-generation", tags=["website-generation"])

# Initialize services
website_template_service = WebsiteTemplateService()


@router.post("/generate-website")
async def generate_website_for_business(
    business_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate an improved website for a low-scoring business
    
    This endpoint takes business data and generates a professional website
    using appropriate templates based on the business niche.
    """
    try:
        logger.info(f"Generating website for business: {business_data.get('business_name', 'Unknown')}")
        
        # Validate required fields
        required_fields = ['business_name', 'location', 'niche']
        missing_fields = [field for field in required_fields if not business_data.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {missing_fields}"
            )
        
        # Check if business has a low score (below 70)
        score = business_data.get('score_overall', 0)
        if score >= 70:
            logger.info(f"Business {business_data.get('business_name')} has good score ({score}), no website generation needed")
            return {
                "success": False,
                "message": f"Business score ({score}) is above threshold (70). No website generation needed.",
                "score": score,
                "threshold": 70
            }
        
        # Generate the website
        result = await website_template_service.generate_website_for_business(business_data)
        
        if result["success"]:
            logger.info(f"Website generated successfully for {business_data.get('business_name')}")
            return {
                "success": True,
                "message": "Website generated successfully",
                "data": result,
                "business_name": business_data.get('business_name'),
                "template_used": result.get('template_type'),
                "files_generated": result.get('generated_files', {}).get('filename')
            }
        else:
            logger.error(f"Failed to generate website: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Website generation failed: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in website generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/list-generated-sites")
async def list_generated_websites() -> Dict[str, Any]:
    """List all generated websites"""
    try:
        result = await website_template_service.list_generated_sites()
        return result
    except Exception as e:
        logger.error(f"Error listing generated sites: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list generated sites: {str(e)}"
        )


@router.get("/download-site/{filename}")
async def download_generated_website(filename: str):
    """Download a generated website file"""
    try:
        # Security check: ensure filename is safe
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Get the file path
        output_dir = Path(__file__).parent.parent.parent.parent / "generated_sites"
        file_path = output_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return the file
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='text/html'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading site {filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download site: {str(e)}"
        )


@router.delete("/delete-site/{filename}")
async def delete_generated_website(filename: str) -> Dict[str, Any]:
    """Delete a generated website"""
    try:
        # Security check: ensure filename is safe
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        result = await website_template_service.delete_generated_site(filename)
        return result
        
    except Exception as e:
        logger.error(f"Error deleting site {filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete site: {str(e)}"
        )


@router.post("/generate-multiple-websites")
async def generate_websites_for_multiple_businesses(
    businesses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate websites for multiple low-scoring businesses
    
    This endpoint processes a list of businesses and generates websites
    for those with scores below 70.
    """
    try:
        logger.info(f"Generating websites for {len(businesses)} businesses")
        
        results = []
        successful = 0
        failed = 0
        
        for business in businesses:
            try:
                # Check if business needs website generation
                score = business.get('score_overall', 0)
                if score < 70:
                    result = await website_template_service.generate_website_for_business(business)
                    if result["success"]:
                        successful += 1
                        results.append({
                            "business_name": business.get('business_name'),
                            "status": "success",
                            "template_used": result.get('template_type'),
                            "filename": result.get('generated_files', {}).get('filename')
                        })
                    else:
                        failed += 1
                        results.append({
                            "business_name": business.get('business_name'),
                            "status": "failed",
                            "error": result.get('error')
                        })
                else:
                    results.append({
                        "business_name": business.get('business_name'),
                        "status": "skipped",
                        "reason": f"Score {score} is above threshold 70"
                    })
                    
            except Exception as e:
                failed += 1
                logger.error(f"Error processing business {business.get('business_name')}: {str(e)}")
                results.append({
                    "business_name": business.get('business_name'),
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_businesses": len(businesses),
            "websites_generated": successful,
            "failed": failed,
            "skipped": len(businesses) - successful - failed,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk website generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Bulk website generation failed: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for website generation service"""
    try:
        # Check if templates directory exists
        templates_dir = Path(__file__).parent.parent.parent / "templates" / "sites"
        templates_exist = templates_dir.exists()
        
        # Check if output directory exists and is writable
        output_dir = Path(__file__).parent.parent.parent.parent / "generated_sites"
        output_writable = output_dir.exists() and os.access(output_dir, os.W_OK)
        
        return {
            "status": "healthy",
            "service": "website-generation",
            "templates_available": templates_exist,
            "output_directory_writable": output_writable,
            "available_templates": list(website_template_service.templates.keys())
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "website-generation",
            "error": str(e)
        }
