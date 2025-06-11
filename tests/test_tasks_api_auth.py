import requests

from test_main import BASE_URL


def test_auth_flow():
    # Регистрация
    register_data = {
        "username": "auth_test_user",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    assert response.status_code == 201

    # Вход
    response = requests.post(f"{BASE_URL}/auth/login", json=register_data)
    assert response.status_code == 200
    tokens = response.json()
    assert 'access_token' in tokens
    assert 'refresh_token' in tokens

    # Доступ к защищенному ресурсу
    headers = {'Authorization': f"Bearer {tokens['access_token']}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()['username'] == "auth_test_user"

    # Выход
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    assert response.status_code == 200

    # Попытка доступа после выхода
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    assert response.status_code == 401

    # Обновление токена
    response = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": tokens['refresh_token']
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()