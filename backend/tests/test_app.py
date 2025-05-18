from src.app import app

def test_get_message():
    client = app.test_client()
    response = client.get('/api/message')
    assert response.status_code == 200
    assert response.json == {"message": "Hello from the backend!"}