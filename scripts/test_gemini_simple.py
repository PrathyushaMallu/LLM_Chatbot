"""
Simple Gemini API test.
"""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.enhanced_llm_service import GeminiService


async def test_gemini_only():
    """Test only Gemini API with your key."""
    print("Testing Gemini API with your key...")
    
    # Your API key
    api_key = "AIzaSyCbObAv5dn1d0Y_soSvxg0mU_POS9vfTPo"
    
    try:
        # Create Gemini service
        gemini_service = GeminiService(api_key)
        
        # Test message
        messages = [{"role": "user", "content": "Hello! Please respond with 'Gemini is working perfectly!' and nothing else."}]
        
        print("Sending test message to Gemini...")
        
        # Try different model names
        models_to_try = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
        
        for model in models_to_try:
            try:
                print(f"\nTrying model: {model}")
                result = await gemini_service.generate_response(
                    messages=messages,
                    model=model,
                    max_tokens=50
                )
                
                print(f"✅ SUCCESS with {model}!")
                print(f"Response: {result['response']}")
                print(f"Tokens used: {result['tokens_used']}")
                print(f"Response time: {result['response_time']:.2f}s")
                break
                
            except Exception as e:
                print(f"❌ Failed with {model}: {str(e)}")
                continue
        else:
            print("❌ All models failed!")
            
    except Exception as e:
        print(f"❌ Service creation failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_gemini_only())