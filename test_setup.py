"""
Simple test script to verify the chatbot application is working.
"""

import sys
import os
import asyncio
import requests
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.health_service import HealthService
from app.services.chat_service import ChatService


def test_health_endpoint():
    """Test the health endpoint."""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            return True
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to FastAPI server. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False


async def test_health_service():
    """Test the health service directly."""
    try:
        health_service = HealthService()
        health_status = await health_service.get_health_status()
        print("✅ Health service is working")
        print(f"   Status: {health_status['status']}")
        return True
    except Exception as e:
        print(f"❌ Health service test failed: {e}")
        return False


async def test_chat_service():
    """Test the chat service directly."""
    try:
        chat_service = ChatService()
        conversation = await chat_service.create_conversation("test_user", "Test Chat")
        print("✅ Chat service is working")
        print(f"   Created conversation: {conversation.conversation_id}")
        return True
    except Exception as e:
        print(f"❌ Chat service test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Testing LLM Chatbot Components...\n")
    
    # Test services directly
    print("Testing Services:")
    health_ok = await test_health_service()
    chat_ok = await test_chat_service()
    
    print("\nTesting API Endpoints:")
    api_ok = test_health_endpoint()
    
    print("\n" + "="*50)
    if all([health_ok, chat_ok, api_ok]):
        print("🎉 All tests passed! The chatbot is ready to use.")
        print("\n📊 Access points:")
        print("   - FastAPI: http://localhost:8000")
        print("   - API Docs: http://localhost:8000/api/v1/docs")
        print("   - Health Check: http://localhost:8000/health")
        print("\n🚀 To start Streamlit frontend:")
        print("   streamlit run app/frontend/streamlit_app.py")
    else:
        print("❌ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())