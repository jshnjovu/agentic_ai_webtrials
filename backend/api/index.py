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
        else:
            response = {
                "message": "Agentic AI LeadGen API running",
                "version": "1.0.0",
                "description": "Business discovery and website scoring API",
                "status": "healthy",
                "endpoints": ["/", "/health", "/test", "/discover_businesses"]
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
