import json
import sqlite3
from datetime import datetime, timedelta


# Генерация тестовых данных
def generate_test_users(num_users=20):
    base_username = "testuser"
    domains = ["example.com", "test.org", "demo.net", "sample.io"]
    first_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Jamie", "Quinn", "Avery", "Skyler"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
                  "Martinez"]

    users = []
    for i in range(1, num_users + 1):
        # Генерация случайных, но детерминированных данных
        domain = domains[i % len(domains)]
        first_name = first_names[i % len(first_names)]
        last_name = last_names[i % len(last_names)]

        user = {
            "id": i,
            "username": f"{base_username}{i}",
            "password": f"P@ssw0rd{i}!",  # Пароли должны быть надежными даже в тестах
            "email": f"{first_name.lower()}.{last_name.lower()}{i}@{domain}",
            "photo_filename": f"user_{i}.jpg" if i % 3 == 0 else None,  # Каждый третий пользователь имеет фото
            "created_at": (datetime.now() - timedelta(days=num_users - i)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (datetime.now() - timedelta(days=(num_users - i) // 2)).strftime("%Y-%m-%d %H:%M:%S"),
            "is_active": i % 5 != 0,  # Каждый пятый пользователь неактивен
            "last_login": (datetime.now() - timedelta(hours=i * 2)).strftime(
                "%Y-%m-%d %H:%M:%S") if i % 4 == 0 else None
        }
        users.append(user)

    return users


# Сохранение в JSON файл
def save_to_json(users, filename="users_fixture.json"):
    with open(filename, 'w') as f:
        json.dump(users, f, indent=2)


# Загрузка в базу данных SQLite
def load_to_database(users, db_file="users.db"):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицу если ее нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            photo_filename TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            last_login TIMESTAMP
        )
    ''')

    # Вставляем данные
    for user in users:
        cursor.execute('''
            INSERT INTO users 
            (id, username, password_hash, email, photo_filename, created_at, updated_at, is_active, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['id'],
            user['username'],
            # В реальном приложении пароль должен быть хеширован
            hash_password(user['password']),  # Функция hash_password из предыдущего кода
            user['email'],
            user['photo_filename'],
            user['created_at'],
            user['updated_at'],
            user['is_active'],
            user['last_login']
        ))

    conn.commit()
    conn.close()


def hash_password(password):
    # Простая функция хеширования для демонстрации
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Генерация и сохранение данных
if __name__ == "__main__":
    test_users = generate_test_users(20)

    # 1. Сохраняем в JSON файл
    save_to_json(test_users)
    print("Generated users_fixture.json with 20 test users")

    # 2. Загружаем в базу данных
    load_to_database(test_users)
    print("Loaded 20 test users into users.db database")