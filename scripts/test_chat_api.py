import requests
import json

API_URL = "http://localhost:8001/api/v1/chat/message"

payload = {
    "conversation_id": None,
    "user_id": "test_user",
    "message": "Hello from automated test",
    "provider": "gemini",
    "model_config": {"model": "local-fallback", "temperature": 0.0, "max_tokens": 100}
}

resp = requests.post(API_URL, json=payload, timeout=20)
try:
    print('Status:', resp.status_code)
    print(json.dumps(resp.json(), indent=2))
except Exception:
    print('Response text:', resp.text)
