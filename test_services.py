#!/usr/bin/env python3
"""
Test script to verify all services and endpoints are working correctly.
"""

import requests
import time
import sys
import json
from typing import Dict, Any


def test_backend_health() -> bool:
    """Test if the FastAPI backend is healthy."""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data}")
            return True
        else:
            print(f"❌ Backend Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Connection Failed: {e}")
        return False


def test_api_endpoints() -> Dict[str, bool]:
    """Test all available API endpoints."""
    base_url = "http://localhost:8001/api/v1"
    results = {}
    
    endpoints = [
        ("GET", "/health", "Health Check"),
        ("GET", "/chat/history", "Chat History"),
        ("GET", "/users/profile", "User Profile"),
        ("GET", "/admin/system/status", "Admin Status"),
        ("GET", "/gemini/providers", "Gemini Providers"),
    ]
    
    for method, path, description in endpoints:
        try:
            url = f"{base_url}{path}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 401, 422]:  # 401/422 are expected for protected endpoints
                print(f"✅ {description}: {response.status_code}")
                results[path] = True
            else:
                print(f"❌ {description}: {response.status_code}")
                results[path] = False
                
        except Exception as e:
            print(f"❌ {description}: Connection Error - {e}")
            results[path] = False
    
    return results


def test_api_documentation() -> bool:
    """Test if API documentation is accessible."""
    try:
        docs_response = requests.get("http://localhost:8001/docs", timeout=5)
        redoc_response = requests.get("http://localhost:8001/redoc", timeout=5)
        
        docs_ok = docs_response.status_code == 200
        redoc_ok = redoc_response.status_code == 200
        
        print(f"✅ API Documentation (Swagger): {'✓' if docs_ok else '✗'}")
        print(f"✅ API Documentation (ReDoc): {'✓' if redoc_ok else '✗'}")
        
        return docs_ok and redoc_ok
    except Exception as e:
        print(f"❌ Documentation Test Failed: {e}")
        return False


def test_openapi_spec() -> bool:
    """Test if OpenAPI specification is available."""
    try:
        response = requests.get("http://localhost:8001/api/v1/openapi.json", timeout=5)
        if response.status_code == 200:
            spec = response.json()
            paths = list(spec.get("paths", {}).keys())
            print(f"✅ OpenAPI Spec Available with {len(paths)} endpoints:")
            for path in sorted(paths)[:10]:  # Show first 10 paths
                print(f"   • {path}")
            if len(paths) > 10:
                print(f"   • ... and {len(paths) - 10} more")
            return True
        else:
            print(f"❌ OpenAPI Spec Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenAPI Spec Test Failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Testing Chatbot Services")
    print("=" * 50)
    
    # Test backend health
    print("\n1. Backend Health Check:")
    backend_healthy = test_backend_health()
    
    if not backend_healthy:
        print("\n❌ Backend is not running! Please start the FastAPI server first.")
        print("   Run: python -c \"import uvicorn; from main import app; uvicorn.run(app, host='localhost', port=8001)\"")
        sys.exit(1)
    
    # Test API endpoints
    print("\n2. API Endpoints Test:")
    endpoint_results = test_api_endpoints()
    
    # Test documentation
    print("\n3. API Documentation Test:")
    docs_ok = test_api_documentation()
    
    # Test OpenAPI spec
    print("\n4. OpenAPI Specification Test:")
    spec_ok = test_openapi_spec()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   • Backend Health: {'✅' if backend_healthy else '❌'}")
    print(f"   • API Endpoints: {sum(endpoint_results.values())}/{len(endpoint_results)} working")
    print(f"   • Documentation: {'✅' if docs_ok else '❌'}")
    print(f"   • OpenAPI Spec: {'✅' if spec_ok else '❌'}")
    
    print("\n🌐 Access Points:")
    print("   • API Server: http://localhost:8001")
    print("   • API Documentation: http://localhost:8001/docs")
    print("   • Alternative Docs: http://localhost:8001/redoc")
    print("   • Streamlit Frontend: http://localhost:8501 (if running)")
    
    if backend_healthy and docs_ok and spec_ok:
        print("\n🎉 All critical services are working correctly!")
    else:
        print("\n⚠️  Some services need attention.")


if __name__ == "__main__":
    main()