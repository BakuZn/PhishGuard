from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

response = client.post("/analyze", json={
    "sender": "test@test.com",
    "subject": "test",
    "body_text": "",
    "body_html": "",
    "links": []
})
print("TEST 1 (Normal):", response.status_code, response.json())

response = client.post("/analyze", json={
    "sender": None,
    "subject": "test",
    "body_text": "",
    "body_html": "",
    "links": []
})
print("TEST 2 (Sender None):", response.status_code, response.json())

response = client.post("/analyze", json={
    "subject": "test",
    "body_text": "",
    "body_html": "",
    "links": []
})
print("TEST 3 (No Sender):", response.status_code, response.json())
