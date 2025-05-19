import pytest
from fastapi.testclient import TestClient
from app.main import app

client= TestClient(app)

def test_register_and_login():
      response= client.post("/register", json={"email":"test@example.com","password":"pass"})
      assert response.status_code==200 or response.status_code==201

      login_response= client.post("/login", json={"email":"test@example.com","password":"pass"})
      assert login_response.status_code==200
      token_data=response.json()
      assert "access_token" in token_data

def test_protected_endpoint():
      # Получить токен и проверить доступ без него и с ним.
      pass
