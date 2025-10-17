"""
Discover available Gemini models.
"""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


async def discover_gemini_models():
    """Discover what Gemini models are actually available."""
    print("Discovering available Gemini models...")
    
    api_key = "AIzaSyCbObAv5dn1d0Y_soSvxg0mU_POS9vfTPo"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        print("Connected to Gemini API. Listing available models...")
        
        # List available models
        models = genai.list_models()
        
        print("\n📋 Available models:")
        chat_models = []
        
        for model in models:
            print(f"  - {model.name}")
            print(f"    Display name: {model.display_name}")
            print(f"    Supported methods: {list(model.supported_generation_methods)}")
            
            # Check if it supports generateContent
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                chat_models.append(model_name)
                print(f"    ✅ Can be used for chat: {model_name}")
            else:
                print(f"    ❌ Cannot be used for chat")
            print()
        
        print(f"\n🎯 Models that support chat (generateContent):")
        for model in chat_models:
            print(f"  - {model}")
        
        # Test the first available chat model
        if chat_models:
            test_model = chat_models[0]
            print(f"\n🧪 Testing with {test_model}...")
            
            model_instance = genai.GenerativeModel(test_model)
            response = await asyncio.to_thread(
                model_instance.generate_content,
                "Hello! Please respond with 'Gemini is working!' and nothing else."
            )
            
            print(f"✅ SUCCESS!")
            print(f"Response: {response.text}")
            
            return test_model
        else:
            print("❌ No chat-capable models found!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(discover_gemini_models())