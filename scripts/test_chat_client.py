import sys
import os
from fastapi.testclient import TestClient
import json

# Ensure project root is on sys.path so `main` can be imported when running from scripts/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app

client = TestClient(app)

payload = {
    "conversation_id": None,
    "user_id": "test_user",
    "message": "Hello from in-process test",
    "provider": "gemini",
    "model": None,
    "model_parameters": {"temperature": 0.7, "max_tokens": 200}
}

resp = client.post("/api/v1/chat/message", json=payload)
print("Status:", resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception:
    print('Response text:', resp.text)
