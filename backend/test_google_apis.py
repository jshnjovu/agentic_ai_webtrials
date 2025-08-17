#!/usr/bin/env python3
"""
Test script to validate Google API keys and check their functionality.
This script tests all Google APIs configured in the environment.
"""

import os
import requests
import json
from typing import Dict, Any, Tuple

def test_google_places_api(api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Test Google Places API with legacy endpoint."""
    try:
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": "San Francisco",
            "inputtype": "textquery",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            if data.get("status") == "OK":
                return True, "API working - Places found", data
            elif data.get("status") == "REQUEST_DENIED":
                return False, "API key valid but API not enabled", data
            else:
                return False, f"API error: {data.get('status')}", data
        else:
            return False, f"HTTP error: {response.status_code}", data
            
    except Exception as e:
        return False, f"Request failed: {str(e)}", {}

def test_google_places_new_api(api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Test Google Places API (New) endpoint."""
    try:
        url = f"https://places.googleapis.com/v1/places:searchText?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {"textQuery": "San Francisco"}
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            return True, "New Places API working", data
        elif response.status_code == 403:
            return False, "API key valid but Places API (New) not enabled", data
        else:
            return False, f"HTTP error: {response.status_code}", data
            
    except Exception as e:
        return False, f"Request failed: {str(e)}", {}

def test_google_geocoding_api(api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Test Google Geocoding API."""
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": "San Francisco",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            if data.get("status") == "OK":
                return True, "Geocoding API working", data
            elif data.get("status") == "REQUEST_DENIED":
                return False, "API key valid but Geocoding API not enabled", data
            else:
                return False, f"API error: {data.get('status')}", data
        else:
            return False, f"HTTP error: {response.status_code}", data
            
    except Exception as e:
        return False, f"Request failed: {str(e)}", {}

def test_google_geolocation_api(api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Test Google Geolocation API."""
    try:
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"
        data = {"considerIp": True}
        
        response = requests.post(url, json=data, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            if "location" in data:
                return True, "Geolocation API working", data
            else:
                return False, "Unexpected response format", data
        elif response.status_code == 404:
            return False, "Geolocation API not enabled", data
        else:
            return False, f"HTTP error: {response.status_code}", data
            
    except Exception as e:
        return False, f"Request failed: {str(e)}", {}

def test_gemini_api(api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Test Google Gemini API."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": "Hello, how are you?"}
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            if "candidates" in data:
                return True, "Gemini API working", data
            else:
                return False, "Unexpected response format", data
        elif response.status_code == 404:
            return False, "Gemini API not enabled", data
        else:
            return False, f"HTTP error: {response.status_code}", data
            
    except Exception as e:
        return False, f"Request failed: {str(e)}", {}

def test_lighthouse_api(api_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Test Google PageSpeed Insights (Lighthouse) API."""
    try:
        url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": "https://www.google.com",
            "key": api_key,
            "strategy": "desktop"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            if "lighthouseResult" in data:
                return True, "Lighthouse API working", data
            else:
                return False, "Unexpected response format", data
        elif response.status_code == 400:
            return False, "API key invalid or malformed", data
        else:
            return False, f"HTTP error: {response.status_code}", data
            
    except Exception as e:
        return False, f"Request failed: {str(e)}", {}

def main():
    """Main function to test all Google APIs."""
    print("🔍 Testing Google API Keys and Functionality")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test results storage
    results = {}
    
    # Test Google Places API
    print("\n📍 Testing Google Places API...")
    places_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if places_key:
        success, message, data = test_google_places_api(places_key)
        results["Google Places API"] = {"success": success, "message": message, "data": data}
        status = "✅" if success else "❌"
        print(f"   {status} {message}")
        
        # Test new Places API
        success_new, message_new, data_new = test_google_places_new_api(places_key)
        results["Google Places API (New)"] = {"success": success_new, "message": message_new, "data": data_new}
        status_new = "✅" if success_new else "❌"
        print(f"   {status_new} {message_new}")
    else:
        print("   ⚠️  No Google Places API key found")
    
    # Test Google General API
    print("\n🌍 Testing Google General API...")
    general_key = os.getenv("GOOGLE_GENERAL_API_KEY")
    if general_key:
        success, message, data = test_google_geocoding_api(general_key)
        results["Google Geocoding API"] = {"success": success, "message": message, "data": data}
        status = "✅" if success else "❌"
        print(f"   {status} {message}")
        
        # Test Geolocation API
        success_geo, message_geo, data_geo = test_google_geolocation_api(general_key)
        results["Google Geolocation API"] = {"success": success_geo, "message": message_geo, "data": data_geo}
        status_geo = "✅" if success_geo else "❌"
        print(f"   {status_geo} {message_geo}")
    else:
        print("   ⚠️  No Google General API key found")
    
    # Test Gemini API
    print("\n🤖 Testing Google Gemini API...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        success, message, data = test_gemini_api(gemini_key)
        results["Google Gemini API"] = {"success": success, "message": message, "data": data}
        status = "✅" if success else "❌"
        print(f"   {status} {message}")
    else:
        print("   ⚠️  No Gemini API key found")
    
    # Test Lighthouse API
    print("\n💡 Testing Google PageSpeed Insights (Lighthouse) API...")
    lighthouse_key = os.getenv("LIGHTHOUSE_API_KEY")
    if lighthouse_key:
        success, message, data = test_lighthouse_api(lighthouse_key)
        results["Google Lighthouse API"] = {"success": success, "message": message, "data": data}
        status = "✅" if success else "❌"
        print(f"   {status} {message}")
    else:
        print("   ⚠️  No Lighthouse API key found")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API Test Summary")
    print("=" * 60)
    
    working_apis = 0
    total_apis = len(results)
    
    for api_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {api_name}: {result['message']}")
        if result["success"]:
            working_apis += 1
    
    print(f"\n🎯 Results: {working_apis}/{total_apis} APIs working")
    
    if working_apis == 0:
        print("\n🚨 All Google APIs are failing! Check your API keys and enable the required APIs.")
    elif working_apis < total_apis:
        print(f"\n⚠️  {total_apis - working_apis} APIs need attention. Check API enablement and permissions.")
    else:
        print("\n🎉 All Google APIs are working perfectly!")
    
    # Save detailed results to file
    with open("google_api_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Detailed results saved to: google_api_test_results.json")

if __name__ == "__main__":
    main()
