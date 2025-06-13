import requests
from typing import Optional
import os

# Базовый URL вашего API
BASE_URL = "http://127.0.0.1:8001"  # Замените на ваш реальный URL


# Функции для работы с аутентификацией
def register_user(username: str, password: str):
    url = f"{BASE_URL}/users/register"
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error registering user: {e}")
        return None


def login_user(username: str, password: str) -> Optional[str]:
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error logging in: {e}")
        return None


# Функции для работы с задачами
def create_task(task_data: dict, token: str):
    url = f"{BASE_URL}/tasks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "title": "Новая задача",
        "description": "Описание задачи 1",
        "priority": "High",
        "status": "Open",
        "responsible_id": 1
    }
    response = requests.get(f"{BASE_URL}/tasks", json=payload, headers=headers)

    assert response.status_code == 200
    print(response.json())

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating task: {e}")
        return None


def add_file(task_data: dict, token: str):
    file_path = "example.pdf"
    url = f"{BASE_URL}/tasks"
    headers = {
        "Authorization": f"Bearer {token}",
    }



    try:
        with open(file_path, "rb") as f:
            files = {"file": ("example.pdf", f, "application/pdf")}
            response = requests.post(url, files=files, headers=headers)

        print(response.status_code)
        print(response.json())

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding file task: {e}")
        return None


def get_user_tasks(token: str):
    url = f"{BASE_URL}/tasks_by_user_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting user tasks: {e}")
        return None


def get_all_tasks():
    url = f"{BASE_URL}/tasks"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting all tasks: {e}")
        return None


def assign_responsible(task_id: int, user_id: int, token: str):
    url = f"{BASE_URL}/tasks/{task_id}/assign"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {"user_id": user_id}
    try:
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error assigning responsible: {e}")
        return None


def update_task(task_id: int, update_data: dict, token: str):
    url = f"{BASE_URL}/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.patch(url, json=update_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating task: {e}")
        return None


# Функции для работы с досками
def create_board(board_name: str, token: str):
    url = f"{BASE_URL}/boards"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json={"title": "Рабочая доска"}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating board: {e}")
        return None


def delete_board(board_id: int, token: str):
    url = f"{BASE_URL}/boards/{board_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error deleting board: {e}")
        return None


def update_board(board_id: int, update_data: dict, token: str):
    url = f"{BASE_URL}/boards/{board_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.patch(url, json=update_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating board: {e}")
        return None


def add_user_to_board(board_id: int, user_id: int, token: str):
    url = f"{BASE_URL}/boards/{board_id}/users/add"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {"user_id": user_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding user to board: {e}")
        return None


def remove_user_from_board(board_id: int, user_id: int, token: str):
    url = f"{BASE_URL}/boards/{board_id}/users/remove"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {"user_id": user_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error removing user from board: {e}")
        return None


def add_task_to_board(board_id: int, task_id: int, token: str):
    url = f"{BASE_URL}/boards/{board_id}/tasks/add"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {"task_id": task_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding task to board: {e}")
        return None


def remove_task_from_board(board_id: int, task_id: int, token: str):
    url = f"{BASE_URL}/boards/{board_id}/tasks/remove"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {"task_id": task_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error removing task from board: {e}")
        return None


def get_board_tasks(board_id: int):
    url = f"{BASE_URL}/boards/{board_id}/tasks"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting board tasks: {e}")
        return None


# Функции для работы с аватарами

def upload_avatar(user_id: int, image_path: str, token: str):
    url = f"{BASE_URL}/users/{user_id}/avatar"
    headers = {
        "Authorization": f"Bearer {token}",
    }

    with open(image_path, "rb") as image_file:
        files = {
            "file": (image_path, image_file, "image/png")  # укажи нужный content-type
        }
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        print("Аватар успешно загружен")
        print(response.json())
        return response.json()
    else:
        print(f"Ошибка загрузки: {response.status_code} - {response.text}")
        return None



def delete_avatar(user_id: int, token: str):
    url = f"{BASE_URL}/users/{user_id}/avatar"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error deleting avatar: {e}")
        return None


# Пример использования
if __name__ == "__main__":
    # # Регистрация и вход
    # print("Registering user...")
    # register_user("testuser", "testpassword")

    print("Logging in...")
    token = login_user("testuser", "testpassword")
    if not token:
        print("Failed to login")
        exit(1)
    # 
    # # Работа с задачами
    # print("Creating task...")
    # task_data = {
    #     "title": "Test Task",
    #     "description": "This is a test task",
    #     "status": "todo",
    #     "priority": "medium"
    # }
    # task = create_task(task_data, token)
    # print(f"Created task: {task}")
    # 
    # print("Getting user tasks...")
    # tasks = get_user_tasks(token)
    # print(f"User tasks: {tasks}")

    # Работа с досками
    # print("Creating board...")
    # board = create_board("Test Board", token)
    # print(f"Created board: {board}")


    # print("Adding task to board...")
    # result = add_task_to_board(1, 1, token)
    # print(f"Add task to board result: {result}")
    #
    # Работа с аватаром
    print("Uploading avatar...")
    avatar_path = "/Users/elenayanushevskaya/QAP/api_server/user_photos/test_photo.jpg"  # Укажите реальный путь к изображению
    if os.path.exists(avatar_path):
        avatar_result = upload_avatar(2, avatar_path, token)  # Предполагаем, что user_id=1
        print(f"Avatar upload result: {avatar_result}")

    # # Удаление аватара
    # print("Deleting avatar...")
    # delete_result = delete_avatar(1, token)  # Предполагаем, что user_id=1
    # print(f"Avatar delete result: {delete_result}")
