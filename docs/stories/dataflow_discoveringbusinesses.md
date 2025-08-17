I'll analyze the current backend API and create a streamlined markdown specification for the "Discover Businesses" functionality based on what's shown in the image and your requirements.

Read file: backend/src/api/v1/business_search.py
Now let me check the current schema to understand what needs to be modified:

Read file: backend/src/schemas/business_search.py
Now let me check if there's a confidence scoring service to understand how to integrate it:

Ran tool
Perfect! Now I have a complete understanding. Let me create the markdown specification for the streamlined "Discover Businesses" API.

# **Discover Businesses API Specification**

## **API Endpoint**
```
POST /api/v1/business-search/google-places/search
GET  /api/v1/business-search/google-places/search
```

## **Request Parameters**

### **POST Request Body**
```json
{
  "query": "gyms",
  "location": "London UK",
  "location_type": "city",
  "category": "gym",
  "radius": 5000,
  "max_results": 10,
  "run_id": "optional-uuid"
}
```

### **GET Request Query Parameters**
- `query` (required): Search query for businesses (1-200 chars)
- `location` (required): Location to search in (city, address, coordinates, or ZIP)
- `location_type` (optional): Type of location input - `"city" | "coordinates" | "address" | "zip_code"` (default: `"city"`)
- `category` (optional): Business category filter (max 100 chars)
- `radius` (optional): Search radius in meters (100-50000, default: 5000)
- `max_results` (optional): Maximum results to return (1-20, default: 10)
- `run_id` (optional): Unique processing run identifier

## **Response Structure**

### **Success Response (200)**
```json
{
  "success": true,
  "query": "gyms",
  "location": "London UK",
  "total_results": 10,
  "results": [
    {
      "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
      "name": "PureGym London Bridge",
      "rating": 4.2,
      "user_ratings_total": 1247,
      "address": "London Bridge, London SE1 9DD, UK",
      "phone": "+44 20 7946 0958",
      "website": "https://www.puregym.com/gyms/london-bridge/",
      "categories": ["gym", "health", "establishment"],
      "confidence_level": "high"
    }
  ],
  "next_page_token": "CqQCFAAAAAA...",
  "run_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### **Error Response (400/500)**
```json
{
  "success": false,
  "error": "Invalid business search request",
  "error_code": "VALIDATION_ERROR",
  "context": "business_search",
  "query": "gyms",
  "location": "London UK",
  "run_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## **Business Data Fields (Streamlined)**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `place_id` | string | ✅ | Google Places unique identifier | `"ChIJN1t_tDeuEmsRUsoyG83frY4"` |
| `name` | string | ✅ | Business name | `"PureGym London Bridge"` |
| `rating` | float | ❌ | Business rating (0.0-5.0) | `4.2` |
| `user_ratings_total` | integer | ❌ | Total number of user ratings | `1247` |
| `address` | string | ❌ | Business address | `"London Bridge, London SE1 9DD, UK"` |
| `phone` | string | ❌ | Business phone number | `"+44 20 7946 0958"` |
| `website` | string | ❌ | Business website URL | `"https://www.puregym.com/gyms/london-bridge/"` |
| `categories` | array[string] | ❌ | Business types/categories | `["gym", "health", "establishment"]` |
| `confidence_level` | string | ✅ | Data quality confidence | `"high" \| "medium" \| "low"` |

## **Confidence Level Values**

- **`"high"`**: 80%+ confidence score - Excellent data quality
- **`"medium"`**: 60-79% confidence score - Good data quality  
- **`"low"`**: Below 60% confidence score - Fair data quality, may need review

## **Confidence Calculation Factors**

The `confidence_level` is computed using our custom algorithm that evaluates:

1. **Name Quality (25%)**: Length, formatting, special characters
2. **Location Accuracy (25%)**: Coordinate validation, address completeness
3. **Contact Information (20%)**: Phone, website, email validation
4. **Rating Data (15%)**: Rating range validation
5. **Categories (10%)**: Number and relevance of business categories
6. **Operating Hours (5%)**: Hours data structure validation

## **Example Usage**

### **Find Gyms in London**
```bash
GET /api/v1/business-search/google-places/search?query=gyms&location=London UK&max_results=10
```

### **Find Restaurants in Soho**
```bash
GET /api/v1/business-search/google-places/search?query=restaurants&location=Soho London&category=restaurant&radius=2000
```

### **Find Coffee Shops Near Coordinates**
```bash
GET /api/v1/business-search/google-places/search?query=coffee&location=51.5074,-0.1278&location_type=coordinates&radius=1000
```

## **Pagination**

- **Default**: Returns up to 10 results per request
- **Next Page**: Use `next_page_token` from response to get additional results
- **Maximum**: Up to 20 results per request (configurable)

## **Rate Limiting**

- **Google Places API**: 1000 requests per day (free tier)
- **Our Service**: Built-in rate limiting with exponential backoff
- **Response Headers**: Include remaining quota and reset time

## **Data Sources**

- **Primary**: Google Places API
- **Fallback**: Yelp Fusion API (if Google Places fails)
- **Enhancement**: Our custom confidence scoring algorithm
- **Merging**: Business data deduplication and merging across sources

This streamlined API provides exactly the data shown in your interface while maintaining the essential fields needed for business discovery and user interaction.