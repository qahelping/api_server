import pytest
import requests
import json

BASE_URL = "http://localhost:5000/api"


@pytest.fixture
def test_user():
    # Создаем тестового пользователя
    user_data = {
        "username": "task_test_user",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    return response.json()


def test_create_task(test_user):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": 3,
        "creator_id": test_user['id']
    }

    response = requests.post(f"{BASE_URL}/tasks", json=task_data)
    assert response.status_code == 201
    assert response.json()['title'] == "Test Task"
    assert response.json()['creator']['id'] == test_user['id']


def test_get_tasks(test_user):
    # Создаем несколько задач
    for i in range(3):
        requests.post(f"{BASE_URL}/tasks", json={
            "title": f"Task {i}",
            "creator_id": test_user['id']
        })

    response = requests.get(f"{BASE_URL}/tasks?creator_id={test_user['id']}")
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_update_task(test_user):
    # Создаем задачу
    task = requests.post(f"{BASE_URL}/tasks", json={
        "title": "Task to update",
        "creator_id": test_user['id']
    }).json()

    # Обновляем задачу
    response = requests.put(f"{BASE_URL}/tasks/{task['id']}", json={
        "status": "in_progress",
        "priority": 1
    })

    assert response.status_code == 200
    assert response.json()['status'] == "in_progress"
    assert response.json()['priority'] == 1


def test_delete_task(test_user):
    # Создаем задачу
    task = requests.post(f"{BASE_URL}/tasks", json={
        "title": "Task to delete",
        "creator_id": test_user['id']
    }).json()

    # Удаляем задачу
    response = requests.delete(f"{BASE_URL}/tasks/{task['id']}")
    assert response.status_code == 200

    # Проверяем, что задача удалена
    response = requests.get(f"{BASE_URL}/tasks/{task['id']}")
    assert response.status_code == 404