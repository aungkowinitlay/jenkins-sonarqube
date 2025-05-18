cat <<EOL > backend/tests/test_app.py
from flask import Flask
from app import app

def test_get_message():
    client = app.test_client()
    response = client.get('/api/message')
    assert response.status_code == 200
    assert response.json == {"message": "Hello from the backend!"}
EOL
