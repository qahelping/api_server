import pytest
import requests

BASE_URL = "http://127.0.0.1:8001"

url = f"{BASE_URL}/users/register"
payload = {
    "username": "user1",
    "password": "password123"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
assert response.status_code == 200


response = requests.post(f"{BASE_URL}/login", json=payload, headers=headers)

data = response.json()
TOKEN = data["access_token"]
print(TOKEN)
headers = {
    "Authorization": f"Bearer {data["access_token"]}",
    "Content-Type": "application/json",
}

response = requests.get(f"{BASE_URL}/tasks", json=payload, headers=headers)

assert response.status_code == 200
print(response.json())


payload = {
    "title": "Новая задача",
    "description": "Описание задачи 1",
    "priority": "High",
    "status": "Open",
    "responsible_id": 1
}
response = requests.post(f"{BASE_URL}/tasks", json=payload, headers=headers)

assert response.status_code == 200
print(response.json())



data = {
    "user_id": 1  # ID пользователя, которого назначаете ответственным
}
task_id = 1
response = requests.put(f"{BASE_URL}/tasks/{task_id}/assign", json=data, headers=headers)

print(response.status_code)
print(response.json())

payload = {
    "status": "In Progress",
}

response = requests.patch(f"{BASE_URL}/tasks/{task_id}", json=payload, headers=headers)

print(response.status_code)
print(response.json())

response = requests.patch(f"{BASE_URL}/tasks/{task_id}", json=payload, headers=headers)

print(response.status_code)
print(response.json())