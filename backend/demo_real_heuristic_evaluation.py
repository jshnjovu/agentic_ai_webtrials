#!/usr/bin/env python3
"""
Demo script for real Heuristic Evaluation API integration.
This script demonstrates the actual implementation using real web scraping and evaluation.

Usage:
    python demo_real_heuristic_evaluation.py [website_url]

Examples:
    python demo_real_heuristic_evaluation.py https://www.google.com
    python demo_real_heuristic_evaluation.py https://www.github.com
    python demo_real_heuristic_evaluation.py https://www.stackoverflow.com
"""

import sys
import time
import json
from src.services.heuristic_evaluation_service import HeuristicEvaluationService
from src.core import get_api_config


def demo_heuristic_evaluation(website_url: str):
    """Demonstrate real heuristic evaluation functionality."""
    
    print(f"🔍 Starting real heuristic evaluation for: {website_url}")
    print("=" * 60)
    
    # Create service instance
    service = HeuristicEvaluationService()
    
    # Generate test IDs
    business_id = "demo-business-123"
    run_id = f"demo-run-{int(time.time())}"
    
    print(f"📊 Business ID: {business_id}")
    print(f"🆔 Run ID: {run_id}")
    print()
    
    try:
        # Run heuristic evaluation
        print("🚀 Running heuristic evaluation...")
        start_time = time.time()
        
        result = service.run_heuristic_evaluation(
            website_url=website_url,
            business_id=business_id,
            run_id=run_id
        )
        
        evaluation_time = time.time() - start_time
        
        print(f"✅ Evaluation completed in {evaluation_time:.2f} seconds")
        print()
        
        if result["success"]:
            print("📈 EVALUATION RESULTS:")
            print("-" * 30)
            
            # Display scores
            scores = result["scores"]
            print(f"🏆 Overall Score: {scores.overall_heuristic_score:.1f}/100")
            print(f"🔒 Trust Score: {scores.trust_score:.1f}/100")
            print(f"💼 CRO Score: {scores.cro_score:.1f}/100")
            print(f"📱 Mobile Score: {scores.mobile_score:.1f}/100")
            print(f"📝 Content Score: {scores.content_score:.1f}/100")
            print(f"👥 Social Score: {scores.social_score:.1f}/100")
            print(f"🎯 Confidence Level: {scores.confidence_level.value.upper()}")
            print()
            
            # Display trust signals
            trust_signals = result["trust_signals"]
            print("🔒 TRUST SIGNALS:")
            print(f"  HTTPS: {'✅' if trust_signals.get('has_https') else '❌'}")
            print(f"  Privacy Policy: {'✅' if trust_signals.get('has_privacy_policy') else '❌'}")
            print(f"  Contact Info: {'✅' if trust_signals.get('has_contact_info') else '❌'}")
            print(f"  Terms of Service: {'✅' if trust_signals.get('has_terms_of_service') else '❌'}")
            print(f"  About Page: {'✅' if trust_signals.get('has_about_page') else '❌'}")
            print()
            
            # Display CRO elements
            cro_elements = result["cro_elements"]
            print("💼 CONVERSION RATE OPTIMIZATION:")
            print(f"  CTA Buttons: {'✅' if cro_elements.get('has_cta_buttons') else '❌'}")
            print(f"  Contact Forms: {'✅' if cro_elements.get('has_contact_forms') else '❌'}")
            print(f"  Pricing Tables: {'✅' if cro_elements.get('has_pricing_tables') else '❌'}")
            print(f"  Testimonials: {'✅' if cro_elements.get('has_testimonials') else '❌'}")
            print()
            
            # Display mobile usability
            mobile_usability = result["mobile_usability"]
            print("📱 MOBILE USABILITY:")
            print(f"  Viewport Meta: {'✅' if mobile_usability.get('has_viewport_meta') else '❌'}")
            print(f"  Touch Targets: {'✅' if mobile_usability.get('has_touch_targets') else '❌'}")
            print(f"  Responsive Design: {'✅' if mobile_usability.get('has_responsive_design') else '❌'}")
            print()
            
            # Display content quality
            content_quality = result["content_quality"]
            print("📝 CONTENT QUALITY:")
            print(f"  Proper Headings: {'✅' if content_quality.get('has_proper_headings') else '❌'}")
            print(f"  Alt Text: {'✅' if content_quality.get('has_alt_text') else '❌'}")
            print(f"  Meta Descriptions: {'✅' if content_quality.get('has_meta_descriptions') else '❌'}")
            print()
            
            # Display social proof
            social_proof = result["social_proof"]
            print("👥 SOCIAL PROOF:")
            print(f"  Social Media Links: {'✅' if social_proof.get('has_social_media_links') else '❌'}")
            print(f"  Customer Reviews: {'✅' if social_proof.get('has_customer_reviews') else '❌'}")
            print(f"  Testimonials: {'✅' if social_proof.get('has_testimonials') else '❌'}")
            print(f"  Case Studies: {'✅' if social_proof.get('has_case_studies') else '❌'}")
            print()
            
            # Display raw data
            raw_data = result.get("raw_data", {})
            if raw_data:
                print("📊 RAW DATA:")
                print(f"  HTML Length: {raw_data.get('html_length', 'N/A')} characters")
                print(f"  Evaluation Time: {raw_data.get('evaluation_time', 'N/A')} seconds")
                print()
            
        else:
            print("❌ EVALUATION FAILED:")
            print(f"  Error: {result.get('error', 'Unknown error')}")
            print(f"  Error Code: {result.get('error_code', 'N/A')}")
            print(f"  Context: {result.get('context', 'N/A')}")
        
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
    
    print("=" * 60)
    print("🎉 Demo completed!")


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python demo_real_heuristic_evaluation.py <website_url>")
        print("Example: python demo_real_heuristic_evaluation.py https://www.google.com")
        sys.exit(1)
    
    website_url = sys.argv[1]
    
    # Validate URL format
    if not website_url.startswith(('http://', 'https://')):
        website_url = 'https://' + website_url
    
    print("🌐 Heuristic Evaluation Demo")
    print("This demo uses REAL web scraping and evaluation (no mocks)")
    print()
    
    demo_heuristic_evaluation(website_url)


if __name__ == "__main__":
    main()
