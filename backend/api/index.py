from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if self.path == '/health':
            response = {
                "status": "healthy",
                "message": "API is running successfully",
                "version": "1.0.0"
            }
        elif self.path == '/test':
            response = {
                "message": "Backend is working!",
                "timestamp": "now"
            }
        elif self.path.startswith('/discover_businesses'):
            # Parse query parameters
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            location = query_params.get('location', [''])[0]
            niche = query_params.get('niche', [''])[0]
            
            if not location or not niche:
                response = {
                    "error": "Missing required parameters",
                    "required": ["location", "niche"],
                    "received": {"location": location, "niche": niche}
                }
            else:
                # Mock business discovery response
                response = {
                    "results": [
                        {
                            "business_name": f"Sample {niche.title()} Business",
                            "website": "https://example.com",
                            "score_overall": 85,
                            "address": f"123 {niche.title()} St, {location}",
                            "phone": "+1-555-0001",
                            "niche": niche,
                            "source": "backend-mock"
                        }
                    ],
                    "total": 1,
                    "success": True,
                    "message": f"Found 1 business in {location} for {niche}",
                    "source": "backend"
                }
        elif self.path.startswith('/api/v1/leadgen-agent/discover-businesses'):
            # Parse query parameters for the new endpoint
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            location = query_params.get('location', [''])[0]
            niche = query_params.get('niche', [''])[0]
            
            if not location or not niche:
                response = {
                    "error": "Missing required parameters",
                    "required": ["location", "niche"],
                    "received": {"location": location, "niche": niche}
                }
            else:
                # Enhanced mock business discovery response matching frontend expectations
                response = {
                    "success": True,
                    "run_id": f"run_{hash(location + niche) % 10000}",
                    "location": location,
                    "niche": niche,
                    "total_discovered": 2,
                    "results": [
                        {
                            "business_name": f"{niche.title()} Business 1 ({location})",
                            "website": "https://example1.com",
                            "score_overall": 75,
                            "address": f"123 Main St, {location}",
                            "phone": "+1-555-0001",
                            "niche": niche,
                            "source": "backend-production",
                            "score_perf": 80,
                            "score_access": 85,
                            "score_seo": 70,
                            "score_trust": 75,
                            "score_cro": 80,
                            "top_issues": ["Mobile responsiveness", "Page load speed", "SEO optimization"]
                        },
                        {
                            "business_name": f"{niche.title()} Business 2 ({location})",
                            "website": "https://example2.com",
                            "score_overall": 65,
                            "address": f"456 Oak Ave, {location}",
                            "phone": "+1-555-0002",
                            "niche": niche,
                            "source": "backend-production",
                            "score_perf": 70,
                            "score_access": 75,
                            "score_seo": 60,
                            "score_trust": 65,
                            "score_cro": 70,
                            "top_issues": ["Content quality", "User experience", "Conversion optimization"]
                        }
                    ]
                }
        else:
            response = {
                "message": "Agentic AI LeadGen API running",
                "version": "1.0.0",
                "description": "Business discovery and website scoring API",
                "status": "healthy",
                "endpoints": ["/", "/health", "/test", "/discover_businesses", "/api/v1/leadgen-agent/discover-businesses"]
            }
        
        self.wfile.write(json.dumps(response).encode())
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
