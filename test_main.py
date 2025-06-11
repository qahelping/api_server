import pytest
import requests

BASE_URL = "http://127.0.0.1:8001"


def test_user_registration():
    url = f"{BASE_URL}/users/register"
    payload = {
        "username": "user1",
        "password": "password123"
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "user1"


def test_user_login():
    url = f"{BASE_URL}/login"
    payload = {
        "username": "user1",
        "password": "password123"
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"



# import time
# import requests
# import subprocess
# import pytest
#
# BASE_URL = "http://127.0.0.1:8001"
# #
# # @pytest.fixture(scope="session", autouse=True)
# # def start_server():
# #     # Запуск FastAPI сервера перед тестами
# #     proc = subprocess.Popen(["uvicorn", "app.main:app"])
# #     time.sleep(2)  # подождать пока сервер поднимется
# #     yield
# #     proc.terminate()
# #     proc.wait()
#
# def test_register_login_and_create_task():
#     # 1. Регистрация
#     res = requests.post(f"{BASE_URL}/register", json={
#         "username": "testuser2",
#         "password": "testpass"
#     })
#     assert res.status_code == 200
#     user_id = res.json()["id"]
#
#     # 2. Логин
#     res = requests.post(f"{BASE_URL}/login", data={
#         "username": "testuser2",
#         "password": "testpass"
#     })
#     assert res.status_code == 200
#     token = res.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}
#
#     # 3. Создание задачи
#     res = requests.post(f"{BASE_URL}/tasks", json={
#         "title": "Task with requests",
#         "description": "Test desc",
#         "priority": "Low",
#         "status": "New",
#         "responsible_id": user_id
#     }, headers=headers)
#     assert res.status_code == 200
#     assert res.json()["title"] == "Task with requests"
#
#     # 4. Получение задач
#     res = requests.get(f"{BASE_URL}/tasks", headers=headers)
#     assert res.status_code == 200
#     assert len(res.json()) >= 1
