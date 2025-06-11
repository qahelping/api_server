from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import hashlib
import os
import uuid
from werkzeug.utils import secure_filename
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# Конфигурация
UPLOAD_FOLDER = 'user_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Создаем папку для фото, если ее нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Декоратор для проверки JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = get_user_by_id(data['user_id'])

            if not current_user:
                return jsonify({'message': 'User not found!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'message': str(e)}), 500

        return f(current_user, *args, **kwargs)

    return decorated

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            photo_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Хеширование пароля
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Метод для создания пользователя
@app.route('/api/users', methods=['POST'])
@token_required
def create_user():
    data = request.form.to_dict()
    file = request.files.get('photo')

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']
    email = data.get('email', '')

    # Обработка фото
    photo_filename = None
    if file and file.filename != '':
        if file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': 'File size exceeds 2MB limit'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Генерируем уникальное имя файла
        ext = file.filename.rsplit('.', 1)[1].lower()
        photo_filename = f"{uuid.uuid4()}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, photo_filename))

    password_hash = hash_password(password)

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, photo_filename)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, photo_filename))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'id': user_id,
            'username': username,
            'email': email,
            'photo_url': f"/api/users/{user_id}/photo" if photo_filename else None,
            'message': 'User created successfully'
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        # Удаляем сохраненное фото если возникла ошибка
        if photo_filename and os.path.exists(os.path.join(UPLOAD_FOLDER, photo_filename)):
            os.remove(os.path.join(UPLOAD_FOLDER, photo_filename))
        return jsonify({'error': str(e)}), 500


# Метод для получения всех пользователей
@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, photo_filename, created_at, updated_at FROM users')
        users = cursor.fetchall()
        conn.close()

        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'photo_url': f"/api/users/{user[0]}/photo" if user[3] else None,
                'created_at': user[4],
                'updated_at': user[5]
            })

        return jsonify(users_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Метод для получения фото пользователя
@app.route('/api/users/<int:user_id>/photo', methods=['GET'])
@token_required
def get_user_photo(user_id):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT photo_filename FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()

        if not result or not result[0]:
            return jsonify({'error': 'Photo not found'}), 404

        filename = result[0]
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Метод для обновления пользователя
@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    try:
        data = request.form.to_dict()
        file = request.files.get('photo')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Получаем текущие данные пользователя
        cursor.execute('SELECT username, email, photo_filename FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        current_username = user[0]
        current_email = user[1]
        current_photo = user[2]

        # Обновляем данные
        username = data.get('username', current_username)
        email = data.get('email', current_email)

        # Обработка пароля (если предоставлен)
        password_hash = None
        if 'password' in data:
            password_hash = hash_password(data['password'])

        # Обработка фото
        photo_filename = current_photo
        if file and file.filename != '':
            if file.content_length > MAX_FILE_SIZE:
                return jsonify({'error': 'File size exceeds 2MB limit'}), 400

            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type'}), 400

            # Удаляем старое фото
            if current_photo and os.path.exists(os.path.join(UPLOAD_FOLDER, current_photo)):
                os.remove(os.path.join(UPLOAD_FOLDER, current_photo))

            # Сохраняем новое фото
            ext = file.filename.rsplit('.', 1)[1].lower()
            photo_filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, photo_filename))

        # Обновляем запись в БД
        if password_hash:
            cursor.execute('''
                UPDATE users 
                SET username = ?, email = ?, password_hash = ?, photo_filename = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (username, email, password_hash, photo_filename, user_id))
        else:
            cursor.execute('''
                UPDATE users 
                SET username = ?, email = ?, photo_filename = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (username, email, photo_filename, user_id))

        conn.commit()
        conn.close()

        return jsonify({
            'id': user_id,
            'username': username,
            'email': email,
            'photo_url': f"/api/users/{user_id}/photo" if photo_filename else None,
            'message': 'User updated successfully'
        })
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Метод для удаления пользователя
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Получаем фото пользователя для удаления
        cursor.execute('SELECT photo_filename FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        # Удаляем запись из БД
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        # Удаляем фото если оно есть
        if result[0] and os.path.exists(os.path.join(UPLOAD_FOLDER, result[0])):
            os.remove(os.path.join(UPLOAD_FOLDER, result[0]))

        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Метод для создания задачи
@app.route('/api/tasks', methods=['POST'])
@token_required
def create_task():
    data = request.get_json()

    required_fields = ['title', 'creator_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Title and creator ID are required'}), 400

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Проверяем существование пользователя-создателя
        cursor.execute('SELECT 1 FROM users WHERE id = ?', (data['creator_id'],))
        if not cursor.fetchone():
            return jsonify({'error': 'Creator not found'}), 404

        # Проверяем существование ответственного (если указан)
        if 'assignee_id' in data and data['assignee_id'] is not None:
            cursor.execute('SELECT 1 FROM users WHERE id = ?', (data['assignee_id'],))
            if not cursor.fetchone():
                return jsonify({'error': 'Assignee not found'}), 404

        cursor.execute('''
            INSERT INTO tasks (title, description, priority, status, due_date, creator_id, assignee_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('description'),
            data.get('priority', 3),  # Средний приоритет по умолчанию
            data.get('status', 'todo'),  # Статус "todo" по умолчанию
            data.get('due_date'),
            data['creator_id'],
            data.get('assignee_id')
        ))

        task_id = cursor.lastrowid
        conn.commit()

        # Получаем полные данные созданной задачи
        cursor.execute('''
            SELECT t.*, u1.username as creator_name, u2.username as assignee_name
            FROM tasks t
            LEFT JOIN users u1 ON t.creator_id = u1.id
            LEFT JOIN users u2 ON t.assignee_id = u2.id
            WHERE t.id = ?
        ''', (task_id,))

        task = cursor.fetchone()
        conn.close()

        if not task:
            return jsonify({'error': 'Task not found after creation'}), 500

        # Форматируем ответ
        task_data = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'priority': task[3],
            'status': task[4],
            'created_at': task[5],
            'due_date': task[6],
            'creator': {
                'id': task[7],
                'username': task[9]
            },
            'assignee': {
                'id': task[8],
                'username': task[10]
            } if task[8] else None
        }

        return jsonify(task_data), 201

    except sqlite3.IntegrityError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Метод для получения списка задач
@app.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Получаем параметры фильтрации из запроса
        status_filter = request.args.get('status')
        assignee_filter = request.args.get('assignee_id')
        creator_filter = request.args.get('creator_id')

        query = '''
            SELECT t.*, u1.username as creator_name, u2.username as assignee_name
            FROM tasks t
            LEFT JOIN users u1 ON t.creator_id = u1.id
            LEFT JOIN users u2 ON t.assignee_id = u2.id
            WHERE 1=1
        '''
        params = []

        if status_filter:
            query += ' AND t.status = ?'
            params.append(status_filter)

        if assignee_filter:
            query += ' AND t.assignee_id = ?'
            params.append(assignee_filter)

        if creator_filter:
            query += ' AND t.creator_id = ?'
            params.append(creator_filter)

        query += ' ORDER BY t.priority ASC, t.created_at DESC'

        cursor.execute(query, params)
        tasks = cursor.fetchall()
        conn.close()

        tasks_list = []
        for task in tasks:
            tasks_list.append({
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'priority': task[3],
                'status': task[4],
                'created_at': task[5],
                'due_date': task[6],
                'creator': {
                    'id': task[7],
                    'username': task[9]
                },
                'assignee': {
                    'id': task[8],
                    'username': task[10]
                } if task[8] else None
            })

        return jsonify(tasks_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Метод для обновления задачи
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(task_id):
    data = request.get_json()

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Проверяем существование задачи
        cursor.execute('SELECT 1 FROM tasks WHERE id = ?', (task_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Task not found'}), 404

        # Проверяем существование нового ответственного (если указан)
        if 'assignee_id' in data and data['assignee_id'] is not None:
            cursor.execute('SELECT 1 FROM users WHERE id = ?', (data['assignee_id'],))
            if not cursor.fetchone():
                return jsonify({'error': 'Assignee not found'}), 404

        # Обновляем только переданные поля
        update_fields = []
        params = []

        if 'title' in data:
            update_fields.append('title = ?')
            params.append(data['title'])

        if 'description' in data:
            update_fields.append('description = ?')
            params.append(data['description'])

        if 'priority' in data:
            update_fields.append('priority = ?')
            params.append(data['priority'])

        if 'status' in data:
            update_fields.append('status = ?')
            params.append(data['status'])

        if 'due_date' in data:
            update_fields.append('due_date = ?')
            params.append(data['due_date'])

        if 'assignee_id' in data:
            update_fields.append('assignee_id = ?')
            params.append(data['assignee_id'])

        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400

        query = 'UPDATE tasks SET ' + ', '.join(update_fields) + ' WHERE id = ?'
        params.append(task_id)

        cursor.execute(query, params)
        conn.commit()

        # Получаем обновлённую задачу
        cursor.execute('''
            SELECT t.*, u1.username as creator_name, u2.username as assignee_name
            FROM tasks t
            LEFT JOIN users u1 ON t.creator_id = u1.id
            LEFT JOIN users u2 ON t.assignee_id = u2.id
            WHERE t.id = ?
        ''', (task_id,))

        task = cursor.fetchone()
        conn.close()

        task_data = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'priority': task[3],
            'status': task[4],
            'created_at': task[5],
            'due_date': task[6],
            'creator': {
                'id': task[7],
                'username': task[9]
            },
            'assignee': {
                'id': task[8],
                'username': task[10]
            } if task[8] else None
        }

        return jsonify(task_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Метод для удаления задачи
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(task_id):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Task not found'}), 404

        conn.close()
        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


from datetime import datetime, timedelta
import jwt
from functools import wraps

app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = 'your-secret-key-here'  # В продакшене используйте сложный ключ
app.config['UPLOAD_FOLDER'] = 'user_photos'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_FILE_SIZE'] = 2 * 1024 * 1024  # 2MB
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Создаем папку для фото, если ее нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



# Вспомогательные функции
def get_user_by_id(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2]
        }
    return None


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            photo_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица задач
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER CHECK(priority BETWEEN 1 AND 5),
            status TEXT CHECK(status IN ('todo', 'in_progress', 'review', 'done')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            creator_id INTEGER NOT NULL,
            assignee_id INTEGER,
            FOREIGN KEY (creator_id) REFERENCES users(id),
            FOREIGN KEY (assignee_id) REFERENCES users(id)
        )
    ''')

    # Таблица для хранения недействительных токенов (для логаута)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS revoked_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jti TEXT UNIQUE NOT NULL,
            revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


# Методы аутентификации
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']
    email = data.get('email', '')

    password_hash = hash_password(password)

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', (username, password_hash, email))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'message': 'User created successfully',
            'user_id': user_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or 'username' not in auth or 'password' not in auth:
        return jsonify({'error': 'Username and password are required'}), 400

    username = auth['username']
    password = auth['password']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_id, password_hash = user

    if hash_password(password) != password_hash:
        return jsonify({'error': 'Invalid password'}), 401

    # Создаем access и refresh токены
    access_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'type': 'access'
    }, app.config['SECRET_KEY'])

    refresh_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + app.config['JWT_REFRESH_TOKEN_EXPIRES'],
        'type': 'refresh'
    }, app.config['SECRET_KEY'])

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user_id
    })


@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = request.headers['Authorization'].split(" ")[1]

    try:
        # Добавляем токен в черный список
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        jti = decoded_token['jti'] if 'jti' in decoded_token else token

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO revoked_tokens (jti) VALUES (?)', (jti,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Successfully logged out'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')

    if not refresh_token:
        return jsonify({'error': 'Refresh token is required'}), 400

    try:
        # Проверяем, что токен не в черном списке
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM revoked_tokens WHERE jti = ?', (refresh_token,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Token has been revoked'}), 401
        conn.close()

        data = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=["HS256"])

        if data['type'] != 'refresh':
            return jsonify({'error': 'Invalid token type'}), 401

        user_id = data['user_id']

        # Создаем новый access токен
        new_access_token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'type': 'access'
        }, app.config['SECRET_KEY'])

        return jsonify({
            'access_token': new_access_token
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Защищенные методы (требуют аутентификации)
@app.route('/api/users/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify(current_user)


@app.route('/api/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    data = request.get_json()

    required_fields = ['title']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Title is required'}), 400

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Проверяем существование ответственного (если указан)
        if 'assignee_id' in data and data['assignee_id'] is not None:
            cursor.execute('SELECT 1 FROM users WHERE id = ?', (data['assignee_id'],))
            if not cursor.fetchone():
                return jsonify({'error': 'Assignee not found'}), 404

        cursor.execute('''
            INSERT INTO tasks (title, description, priority, status, due_date, creator_id, assignee_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('description'),
            data.get('priority', 3),
            data.get('status', 'todo'),
            data.get('due_date'),
            current_user['id'],
            data.get('assignee_id')
        ))

        task_id = cursor.lastrowid
        conn.commit()

        # Получаем полные данные созданной задачи
        cursor.execute('''
            SELECT t.*, u1.username as creator_name, u2.username as assignee_name
            FROM tasks t
            LEFT JOIN users u1 ON t.creator_id = u1.id
            LEFT JOIN users u2 ON t.assignee_id = u2.id
            WHERE t.id = ?
        ''', (task_id,))

        task = cursor.fetchone()
        conn.close()

        if not task:
            return jsonify({'error': 'Task not found after creation'}), 500

        task_data = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'priority': task[3],
            'status': task[4],
            'created_at': task[5],
            'due_date': task[6],
            'creator': {
                'id': task[7],
                'username': task[9]
            },
            'assignee': {
                'id': task[8],
                'username': task[10]
            } if task[8] else None
        }

        return jsonify(task_data), 201

    except sqlite3.IntegrityError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Инициализация API
api = Api(
    app,
    version='1.0',
    title='Trello-like API',
    description='A simple Trello-like API with JWT authentication',
    doc='/swagger/'
)

# Пространство имен для аутентификации
auth_ns = api.namespace('auth', description='Authentication operations')
users_ns = api.namespace('users', description='User operations')
tasks_ns = api.namespace('tasks', description='Task operations')

# Модели для Swagger
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='User identifier'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(description='Email address'),
    'photo_url': fields.String(description='URL to user photo')
})

task_model = api.model('Task', {
    'id': fields.Integer(readOnly=True, description='Task identifier'),
    'title': fields.String(required=True, description='Task title'),
    'description': fields.String(description='Task description'),
    'priority': fields.Integer(description='Priority (1-5)', enum=[1, 2, 3, 4, 5]),
    'status': fields.String(description='Task status', enum=['todo', 'in_progress', 'review', 'done']),
    'created_at': fields.DateTime(description='Creation date'),
    'due_date': fields.DateTime(description='Due date'),
    'creator': fields.Nested(user_model, description='Task creator'),
    'assignee': fields.Nested(user_model, description='Task assignee', allow_null=True)
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

token_model = api.model('Token', {
    'access_token': fields.String(description='Access token'),
    'refresh_token': fields.String(description='Refresh token'),
    'user_id': fields.Integer(description='User ID')
})

# Пример защищенного эндпоинта в Swagger
@tasks_ns.route('/')
class TaskList(Resource):
    @tasks_ns.doc('list_tasks')
    @tasks_ns.marshal_list_with(task_model)
    @tasks_ns.doc(security='Bearer')
    @token_required
    def get(self, current_user):
        """List all tasks"""
        # Ваш код получения задач

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)