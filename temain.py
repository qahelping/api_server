import requests
from typing import Optional, List, Dict, Any

from func import BASE_URL


# Замените на ваш базовый URL API


def login_user(username: str, password: str) -> Optional[str]:
    """Аутентификация пользователя и получение токена"""
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        token = response.json().get("access_token")
        print(f"Успешный вход. Токен: {token}")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Ошибка входа: {e}")
        return None


def create_admin_user(token: str, email: str, password: str) -> Optional[Dict[str, Any]]:
    """Создание администратора (требует прав администратора)"""
    url = f"{BASE_URL}/admin/create"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "email": email,
        "password": password
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        admin = response.json()
        print(f"Администратор создан: {admin}")
        return admin
    except requests.exceptions.RequestException as e:
        print(f"Ошибка создания администратора: {e}")
        return None


def register_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Регистрация нового пользователя"""
    url = f"{BASE_URL}/users/register"
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        user = response.json()
        print(f"Пользователь зарегистрирован: {user}")
        return user
    except requests.exceptions.RequestException as e:
        print(f"Ошибка регистрации: {e}")
        return None


def create_task(token: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Создание задачи"""
    url = f"{BASE_URL}/tasks"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, json=task_data, headers=headers)
        response.raise_for_status()
        task = response.json()
        print(f"Задача создана: {task}")
        return task
    except requests.exceptions.RequestException as e:
        print(f"Ошибка создания задачи: {e}")
        return None


def get_user_tasks(token: str) -> Optional[List[Dict[str, Any]]]:
    """Получение задач пользователя"""
    url = f"{BASE_URL}/tasks_by_user_id"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tasks = response.json()
        print(f"Задачи пользователя: {tasks}")
        return tasks
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения задач: {e}")
        return None


def get_all_tasks() -> Optional[List[Dict[str, Any]]]:
    """Получение всех задач"""
    url = f"{BASE_URL}/tasks"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tasks = response.json()
        print(f"Все задачи: {tasks}")
        return tasks
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения всех задач: {e}")
        return None


def assign_responsible(token: str, task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Назначение ответственного для задачи"""
    url = f"{BASE_URL}/tasks/{task_id}/assign"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"user_id": user_id}
    try:
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()
        task = response.json()
        print(f"Ответственный назначен: {task}")
        return task
    except requests.exceptions.RequestException as e:
        print(f"Ошибка назначения ответственного: {e}")
        return None


def update_task(token: str, task_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обновление задачи"""
    url = f"{BASE_URL}/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        response.raise_for_status()
        task = response.json()
        print(f"Задача обновлена: {task}")
        return task
    except requests.exceptions.RequestException as e:
        print(f"Ошибка обновления задачи: {e}")
        return None


def create_board(token: str, name: str) -> Optional[Dict[str, Any]]:
    """Создание доски"""
    url = f"{BASE_URL}/boards"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        board = response.json()
        print(f"Доска создана: {board}")
        return board
    except requests.exceptions.RequestException as e:
        print(f"Ошибка создания доски: {e}")
        return None


def get_board(board_id: int) -> Optional[Dict[str, Any]]:
    """Получение доски по ID"""
    url = f"{BASE_URL}/boards/{board_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        board = response.json()
        print(f"Доска: {board}")
        return board
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения доски: {e}")
        return None


def update_board(token: str, board_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обновление доски"""
    url = f"{BASE_URL}/boards/{board_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        response.raise_for_status()
        board = response.json()
        print(f"Доска обновлена: {board}")
        return board
    except requests.exceptions.RequestException as e:
        print(f"Ошибка обновления доски: {e}")
        return None


def delete_board(token: str, board_id: int) -> bool:
    """Удаление доски"""
    url = f"{BASE_URL}/boards/{board_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        print(f"Доска {board_id} удалена")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка удаления доски: {e}")
        return False


def add_user_to_board(token: str, board_id: int, user_id: int) -> bool:
    """Добавление пользователя в доску"""
    url = f"{BASE_URL}/boards/{board_id}/users/add"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"user_id": user_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Пользователь {user_id} добавлен в доску {board_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка добавления пользователя в доску: {e}")
        return False


def remove_user_from_board(token: str, board_id: int, user_id: int) -> bool:
    """Удаление пользователя из доски"""
    url = f"{BASE_URL}/boards/{board_id}/users/remove"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"user_id": user_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Пользователь {user_id} удален из доски {board_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка удаления пользователя из доски: {e}")
        return False


def add_task_to_board(token: str, board_id: int, task_id: int) -> bool:
    """Добавление задачи в доску"""
    url = f"{BASE_URL}/boards/{board_id}/tasks/add"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"task_id": task_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Задача {task_id} добавлена в доску {board_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка добавления задачи в доску: {e}")
        return False


def remove_task_from_board(token: str, board_id: int, task_id: int) -> bool:
    """Удаление задачи из доски"""
    url = f"{BASE_URL}/boards/{board_id}/tasks/remove"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"task_id": task_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Задача {task_id} удалена из доски {board_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка удаления задачи из доски: {e}")
        return False


def get_board_tasks(board_id: int) -> Optional[List[Dict[str, Any]]]:
    """Получение задач доски"""
    url = f"{BASE_URL}/boards/{board_id}/tasks"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tasks = response.json()
        print(f"Задачи доски {board_id}: {tasks}")
        return tasks
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения задач доски: {e}")
        return None


def upload_user_avatar(token: str, user_id: int, file_path: str) -> Optional[Dict[str, Any]]:
    """Загрузка аватара пользователя"""
    url = f"{BASE_URL}/users/{user_id}/avatar"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.split('/')[-1], f)}
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            user = response.json()
            print(f"Аватар загружен: {user}")
            return user
    except Exception as e:
        print(f"Ошибка загрузки аватара: {e}")
        return None


def delete_user_avatar(token: str, user_id: int) -> Optional[Dict[str, Any]]:
    """Удаление аватара пользователя"""
    url = f"{BASE_URL}/users/{user_id}/avatar"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        user = response.json()
        print(f"Аватар удален: {user}")
        return user
    except requests.exceptions.RequestException as e:
        print(f"Ошибка удаления аватара: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Получение пользователя по ID"""
    url = f"{BASE_URL}/users/{user_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        user = response.json()
        print(f"Пользователь: {user}")
        return user
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения пользователя: {e}")
        return None


def update_user(token: str, user_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обновление данных пользователя"""
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.patch(url, json=update_data, headers=headers)
        response.raise_for_status()
        user = response.json()
        print(f"Пользователь обновлен: {user}")
        return user
    except requests.exceptions.RequestException as e:
        print(f"Ошибка обновления пользователя: {e}")
        return None


def delete_user(token: str, user_id: int) -> bool:
    """Удаление пользователя"""
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        print(f"Пользователь {user_id} удален")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка удаления пользователя: {e}")
        return False


def get_all_users() -> Optional[List[Dict[str, Any]]]:
    """Получение всех пользователей"""
    url = f"{BASE_URL}/users"
    try:
        response = requests.get(url)
        response.raise_for_status()
        users = response.json()
        print(f"Все пользователи: {users}")
        return users
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения пользователей: {e}")
        return None


def upload_task_pdf(task_id: int, file_path: str) -> bool:
    """Загрузка PDF для задачи"""
    url = f"{BASE_URL}/tasks/{task_id}/upload_pdf"
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.split('/')[-1], f)}
            response = requests.post(url, files=files)
            response.raise_for_status()
            print(f"PDF загружен для задачи {task_id}")
            return True
    except Exception as e:
        print(f"Ошибка загрузки PDF: {e}")
        return False


def delete_task_pdf(task_id: int) -> bool:
    """Удаление PDF задачи"""
    url = f"{BASE_URL}/tasks/{task_id}/delete_pdf"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        print(f"PDF удален для задачи {task_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка удаления PDF: {e}")
        return False


def main():
    # Пример последовательного вызова функций
    print("=== Пример работы с API ===")

    # 1. Регистрация и вход
    print("\n1. Регистрация и вход")
    user = register_user("testuser", "testpassword")
    if not user:
        return

    token = login_user("testuser", "testpassword")
    if not token:
        return

    # 2. Работа с задачами
    print("\n2. Работа с задачами")
    task_data = {
        "title": "Новая задача",
        "description": "Описание задачи",
        "status": "todo"
    }
    task = create_task(token, task_data)
    if task:
        task_id = task["id"]
        update_task(token, task_id, {"status": "in_progress"})
        get_user_tasks(token)
        get_all_tasks()

    # 3. Работа с досками
    print("\n3. Работа с досками")
    board = create_board(token, "Новая доска")
    if board:
        board_id = board["id"]
        get_board(board_id)
        update_board(token, board_id, {"name": "Обновленная доска"})
        add_task_to_board(token, board_id, task_id)
        get_board_tasks(board_id)
        remove_task_from_board(token, board_id, task_id)

    # 4. Работа с пользователями
    print("\n4. Работа с пользователями")
    get_all_users()
    if user:
        update_user(token, user["id"], {"email": "newemail@example.com"})
        get_user_by_id(user["id"])

    # 5. Работа с файлами
    print("\n5. Работа с файлами")
    if task:
        # upload_task_pdf(task["id"], "example.pdf")  # Раскомментируйте если есть PDF для теста
        # delete_task_pdf(task["id"])
        pass

    # 6. Очистка (удаление тестовых данных)
    print("\n6. Очистка")
    if board:
        delete_board(token, board_id)
    if user:
        delete_user(token, user["id"])


if __name__ == "__main__":
    main()