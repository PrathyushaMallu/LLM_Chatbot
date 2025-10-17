"""
Test script for Gemini API integration.
"""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.enhanced_llm_service import enhanced_llm_service, LLMProvider
from app.models.chat_models import LLMConfig


async def test_gemini_integration():
    """Test Gemini API integration."""
    print("Testing Gemini API Integration...")
    
    # Test 1: Check available providers
    print("\n1. Available providers:")
    providers = enhanced_llm_service.get_available_providers()
    print(f"   Available: {providers}")
    
    # Test 2: Test provider health
    print("\n2. Testing provider health:")
    for provider_name in providers:
        provider = LLMProvider(provider_name)
        health = await enhanced_llm_service.test_provider_connection(provider)
        print(f"   {provider_name}: {health['status']} - {health['message']}")
    
    # Test 3: Test OpenAI (if available)
    if LLMProvider.OPENAI in [LLMProvider(p) for p in providers]:
        print("\n3. Testing OpenAI:")
        try:
            messages = [{"role": "user", "content": "Say 'OpenAI is working' in exactly those words."}]
            result = await enhanced_llm_service.generate_response(
                messages=messages,
                provider=LLMProvider.OPENAI,
                config=LLMConfig(max_tokens=50)
            )
            print(f"   Response: {result['response']}")
            print(f"   Model: {result['model']}")
            print(f"   Tokens: {result['tokens_used']}")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    # Test 4: Test Gemini (if available)
    if LLMProvider.GEMINI in [LLMProvider(p) for p in providers]:
        print("\n4. Testing Gemini:")
        try:
            messages = [{"role": "user", "content": "Say 'Gemini is working' in exactly those words."}]
            result = await enhanced_llm_service.generate_response(
                messages=messages,
                provider=LLMProvider.GEMINI,
                config=LLMConfig(model="gemini-pro", max_tokens=50)
            )
            print(f"   Response: {result['response']}")
            print(f"   Model: {result['model']}")
            print(f"   Tokens: {result['tokens_used']}")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    # Test 5: List available models
    print("\n5. Available models:")
    for provider_name in providers:
        provider = LLMProvider(provider_name)
        models = await enhanced_llm_service.list_available_models(provider)
        print(f"   {provider_name}: {models}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(test_gemini_integration())