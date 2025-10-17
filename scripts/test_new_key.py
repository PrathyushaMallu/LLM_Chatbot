"""
Quick test of Gemini API with the new key.
"""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


async def quick_gemini_test():
    """Quick test of Gemini with the current API key."""
    print("🧪 Quick Gemini API Test...")
    
    try:
        import google.generativeai as genai
        
        # Use the API key from environment
        from config.settings import settings
        api_key = settings.gemini_api_key
        
        if not api_key or api_key == "your-gemini-api-key-here":
            print("❌ No valid Gemini API key configured")
            return
        
        print(f"🔑 Using API key: {api_key[:10]}...")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try the current stable model
        models_to_try = ["gemini-2.5-flash", "gemini-pro-latest", "gemini-flash-latest"]
        
        for model_name in models_to_try:
            try:
                print(f"\n📡 Testing model: {model_name}")
                
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(
                    model.generate_content,
                    "Say 'Hello from Gemini!' and tell me which model you are."
                )
                
                print(f"✅ SUCCESS with {model_name}!")
                print(f"📝 Response: {response.text}")
                
                # Test our enhanced service
                print(f"\n🔧 Testing Enhanced LLM Service...")
                from app.services.enhanced_llm_service import enhanced_llm_service, LLMProvider
                from app.models.chat_models import LLMConfig
                
                messages = [{"role": "user", "content": "Hello! Please confirm you are working."}]
                config = LLMConfig(model=model_name, max_tokens=100)
                
                result = await enhanced_llm_service.generate_response(
                    messages=messages,
                    provider=LLMProvider.GEMINI,
                    config=config
                )
                
                print(f"✅ Enhanced service SUCCESS!")
                print(f"📝 Response: {result['response']}")
                print(f"🤖 Model: {result['model']}")
                print(f"⚡ Provider: {result['provider']}")
                print(f"🔢 Tokens: {result['tokens_used']}")
                print(f"⏱️ Time: {result['response_time']:.2f}s")
                
                return True
                
            except Exception as e:
                print(f"❌ Failed with {model_name}: {str(e)}")
                continue
        
        print("❌ All models failed!")
        return False
        
    except Exception as e:
        print(f"❌ General error: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(quick_gemini_test())
    if success:
        print("\n🎉 Gemini integration is working perfectly!")
    else:
        print("\n⚠️ Gemini integration needs attention.")