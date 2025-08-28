curl -s -X POST "https://places.googleapis.com/v1/places:searchText"   -H "Content-Type: application/json"   -H "X-Goog-Api-Key: xxapi"   -H "X-Goog-FieldMask: places.displayName,places.formattedAddress,places.id"   -d '{
    "textQuery": "coffee shops in Nairobi",
    "maxResultCount": 5
  }' | jq .