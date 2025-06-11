import pytest
import requests
import sqlite3
import os
from time import sleep
import io

BASE_URL = "http://localhost:5001/api/users"
TEST_PHOTO_PATH = 'user_photos/test_photo.jpg'  # Создайте тестовый файл или используйте существующий


# Фикстура для очистки базы данных перед каждым тестом
@pytest.fixture(autouse=True)
def cleanup_db():
    sleep(0.1)
    if os.path.exists("users.db"):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
        conn.close()

    # Очищаем папку с фото (кроме .gitkeep)
    for filename in os.listdir("user_photos"):
        if filename != ".gitkeep":
            os.remove(os.path.join("user_photos", filename))


def test_create_user_with_photo():
    # Создаем тестовый файл
    with open(TEST_PHOTO_PATH, 'wb') as f:
        f.write(b'\x00' * 100)  # Просто небольшой файл

    with open(TEST_PHOTO_PATH, 'rb') as f:
        response = requests.post(
            BASE_URL,
            data={
                'username': 'user_with_photo',
                'password': 'testpass',
                'email': 'photo@test.com'
            },
            files={'photo': f}
        )

    assert response.status_code == 201
    assert response.json()['photo_url'] is not None

    # Проверяем, что фото доступно по URL
    user_id = response.json()['id']
    photo_response = requests.get(f"{BASE_URL}/{user_id}/photo")
    assert photo_response.status_code == 200
    assert photo_response.headers['Content-Type'] == 'image/jpeg'


def test_get_all_users():
    # Создаем несколько пользователей
    users = [
        {'username': 'user1', 'password': 'pass1'},
        {'username': 'user2', 'password': 'pass2', 'email': 'user2@test.com'},
        {'username': 'user3', 'password': 'pass3',
         'photo': open(TEST_PHOTO_PATH, 'rb') if os.path.exists(TEST_PHOTO_PATH) else None}
    ]

    for user in users:
        files = {}
        if 'photo' in user and user['photo']:
            files['photo'] = user['photo']
            if hasattr(user['photo'], 'seek'):
                user['photo'].seek(0)

        data = {k: v for k, v in user.items() if k != 'photo'}
        response = requests.post(BASE_URL, data=data, files=files)
        assert response.status_code == 201

    # Получаем список пользователей
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert len(response.json()) == 3

    # Проверяем, что фото есть только у третьего пользователя
    users = response.json()
    photo_users = [u for u in users if u['photo_url'] is not None]
    assert len(photo_users) == (1 if os.path.exists(TEST_PHOTO_PATH) else 0)


def test_update_user():
    # Создаем пользователя
    user_data = {
        'username': 'user_to_update',
        'password': 'original_pass',
        'email': 'original@test.com'
    }
    response = requests.post(BASE_URL, data=user_data)
    user_id = response.json()['id']

    # Обновляем данные
    update_data = {
        'username': 'updated_username',
        'email': 'updated@test.com',
        'password': 'new_password'
    }
    response = requests.put(f"{BASE_URL}/{user_id}", data=update_data)
    assert response.status_code == 200
    assert response.json()['username'] == 'updated_username'
    assert response.json()['email'] == 'updated@test.com'

    # Проверяем, что пароль изменился (через попытку входа)
    # В реальном приложении нужно добавить метод аутентификации


def test_update_user_photo():
    if not os.path.exists(TEST_PHOTO_PATH):
        pytest.skip("Test photo file not found")

    # Создаем пользователя без фото
    user_data = {
        'username': 'user_to_update_photo',
        'password': 'testpass'
    }
    response = requests.post(BASE_URL, data=user_data)
    user_id = response.json()['id']
    assert response.json()['photo_url'] is None

    # Добавляем фото
    with open(TEST_PHOTO_PATH, 'rb') as f:
        response = requests.put(
            f"{BASE_URL}/{user_id}",
            data={'username': 'user_to_update_photo'},
            files={'photo': f}
        )
    assert response.status_code == 200
    assert response.json()['photo_url'] is not None

    # Проверяем, что фото доступно
    photo_response = requests.get(response.json()['photo_url'])
    assert photo_response.status_code == 200


def test_delete_user():
    # Создаем пользователя с фото
    if os.path.exists(TEST_PHOTO_PATH):
        with open(TEST_PHOTO_PATH, 'rb') as f:
            response = requests.post(
                BASE_URL,
                data={
                    'username': 'user_to_delete',
                    'password': 'testpass'
                },
                files={'photo': f}
            )
    else:
        response = requests.post(
            BASE_URL,
            data={
                'username': 'user_to_delete',
                'password': 'testpass'
            }
        )

    user_id = response.json()['id']

    # Удаляем пользователя
    response = requests.delete(f"{BASE_URL}/{user_id}")
    assert response.status_code == 200

    # Проверяем, что пользователя больше нет
    response = requests.get(f"{BASE_URL}/{user_id}/photo")
    assert response.status_code == 404

    response = requests.get(BASE_URL)
    users = [u for u in response.json() if u['id'] == user_id]
    assert len(users) == 0


def test_upload_user_photo():
    with open('user_photos/test_photo.jpg', 'rb') as f:
        response = requests.post(
            '/api/users',
            data={
                'username': 'photouser',
                'password': 'testpass',
                'email': 'photo@test.com'
            },
            files={'photo': f}
        )
    assert response.status_code == 201
    assert response.json()['photo_url'] is not None