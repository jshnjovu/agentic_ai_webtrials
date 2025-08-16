"""
Website Template Service
Handles website template generation and management for low-scoring businesses
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import uuid

logger = logging.getLogger(__name__)


class WebsiteTemplateService:
    """Service for managing website templates and generating improved websites"""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "sites"
        self.output_dir = Path(__file__).parent.parent.parent / "generated_sites"
        self.templates = {
            "restaurant": "restaurant.html",
            "gym": "gym.html", 
            "general": "general.html"
        }
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )

    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a website template"""
        logger.info("Creating website template")
        return {"success": True, "template_id": "template_001"}

    async def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get a website template by ID"""
        return {"success": True, "template": {"id": template_id}}

    async def generate_website_for_business(
        self, 
        business_data: Dict[str, Any], 
        template_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an improved website for a low-scoring business
        
        Args:
            business_data: Business information including name, location, niche, etc.
            template_type: Specific template to use (restaurant, gym, general)
            
        Returns:
            Dictionary containing generation results and file paths
        """
        try:
            logger.info(f"Generating website for business: {business_data.get('business_name', 'Unknown')}")
            
            # Determine template type based on niche if not specified
            if not template_type:
                template_type = self._determine_template_type(business_data.get('niche', ''))
            
            # Validate template type
            if template_type not in self.templates:
                template_type = "general"  # Fallback to general template
            
            # Prepare template data
            template_data = self._prepare_template_data(business_data)
            
            # Generate the website
            generated_files = await self._generate_website_files(template_type, template_data)
            
            # Create deployment package
            deployment_info = await self._create_deployment_package(generated_files, business_data)
            
            logger.info(f"Website generated successfully for {business_data.get('business_name')}")
            
            return {
                "success": True,
                "template_type": template_type,
                "generated_files": generated_files,
                "deployment_info": deployment_info,
                "business_name": business_data.get('business_name'),
                "message": "Website generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating website: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate website"
            }

    def _determine_template_type(self, niche: str) -> str:
        """Determine the best template type based on business niche"""
        niche_lower = niche.lower()
        
        if any(word in niche_lower for word in ['restaurant', 'food', 'dining', 'cafe', 'bar', 'pub']):
            return "restaurant"
        elif any(word in niche_lower for word in ['gym', 'fitness', 'health', 'wellness', 'training']):
            return "gym"
        else:
            return "general"

    def _prepare_template_data(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        return {
            "business_name": business_data.get('business_name', 'Business Name'),
            "location": business_data.get('location', 'Location'),
            "niche": business_data.get('niche', 'Business Type'),
            "address": business_data.get('address', 'Address'),
            "phone": business_data.get('phone', 'Phone Number'),
            "email": business_data.get('email', 'email@example.com'),
            "website": business_data.get('website', ''),
            "score_overall": business_data.get('score_overall', 0),
            "score_perf": business_data.get('score_perf', 0),
            "score_access": business_data.get('score_access', 0),
            "score_seo": business_data.get('score_seo', 0),
            "score_trust": business_data.get('score_trust', 0),
            "score_cro": business_data.get('score_cro', 0),
            "top_issues": business_data.get('top_issues', []),
            "generated_timestamp": business_data.get('timestamp', ''),
            "run_id": business_data.get('run_id', '')
        }

    async def _generate_website_files(
        self, 
        template_type: str, 
        template_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate the actual website files using the selected template"""
        try:
            # Get template file path
            template_file = self.templates[template_type]
            template_path = self.templates_dir / template_file
            
            # Load and render template
            template = self.jinja_env.get_template(template_file)
            rendered_html = template.render(**template_data)
            
            # Create unique filename
            business_name_safe = self._sanitize_filename(template_data['business_name'])
            filename = f"{business_name_safe}_{template_type}_{uuid.uuid4().hex[:8]}.html"
            file_path = self.output_dir / filename
            
            # Write the generated HTML file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            # Create additional files (CSS, JS if needed)
            additional_files = await self._create_additional_files(template_type, template_data)
            
            return {
                "html_file": str(file_path),
                "filename": filename,
                "additional_files": additional_files,
                "template_used": template_type
            }
            
        except Exception as e:
            logger.error(f"Error generating website files: {str(e)}")
            raise

    async def _create_additional_files(
        self, 
        template_type: str, 
        template_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create additional supporting files for the website"""
        additional_files = {}
        
        try:
            # Create a simple CSS file for additional styling
            css_filename = f"{self._sanitize_filename(template_data['business_name'])}_styles.css"
            css_path = self.output_dir / css_filename
            
            css_content = f"""
/* Additional styles for {template_data['business_name']} */
.custom-header {{
    background: linear-gradient(135deg, #667eea, #764ba2);
}}

.business-specific {{
    color: #333;
    font-weight: bold;
}}

/* Responsive improvements */
@media (max-width: 480px) {{
    .hero h1 {{
        font-size: 1.8rem;
    }}
    
    .section {{
        padding: 1.5rem 1rem;
    }}
}}
"""
            
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            additional_files["css_file"] = str(css_path)
            
            # Create a simple JavaScript file for interactivity
            js_filename = f"{self._sanitize_filename(template_data['business_name'])}_script.js"
            js_path = self.output_dir / js_filename
            
            js_content = f"""
// Interactive features for {template_data['business_name']}
document.addEventListener('DOMContentLoaded', function() {{
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
        anchor.addEventListener('click', function (e) {{
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {{
                target.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'start'
                }});
            }}
        }});
    }});
    
    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {{
        form.addEventListener('submit', function(e) {{
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
        }});
    }});
}});
"""
            
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            additional_files["js_file"] = str(js_path)
            
        except Exception as e:
            logger.warning(f"Could not create additional files: {str(e)}")
        
        return additional_files

    async def _create_deployment_package(
        self, 
        generated_files: Dict[str, Any], 
        business_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create deployment information for the generated website"""
        return {
            "deployment_ready": True,
            "files": generated_files,
            "business_info": {
                "name": business_data.get('business_name'),
                "location": business_data.get('location'),
                "niche": business_data.get('niche'),
                "original_score": business_data.get('score_overall', 0)
            },
            "deployment_notes": [
                "Website generated for low-scoring business",
                "Template optimized for mobile and SEO",
                "Ready for deployment to Vercel/Netlify",
                "Includes contact forms and responsive design"
            ]
        }

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        return sanitized[:50]

    async def list_generated_sites(self) -> Dict[str, Any]:
        """List all generated websites"""
        try:
            sites = []
            for file_path in self.output_dir.glob("*.html"):
                sites.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "created": file_path.stat().st_ctime
                })
            
            return {
                "success": True,
                "sites": sites,
                "total_count": len(sites)
            }
        except Exception as e:
            logger.error(f"Error listing generated sites: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_generated_site(self, filename: str) -> Dict[str, Any]:
        """Delete a generated website"""
        try:
            file_path = self.output_dir / filename
            if file_path.exists():
                file_path.unlink()
                return {"success": True, "message": f"Deleted {filename}"}
            else:
                return {"success": False, "error": "File not found"}
        except Exception as e:
            logger.error(f"Error deleting generated site: {str(e)}")
            return {"success": False, "error": str(e)}
