# Trello-like API

Простое API для управления задачами с JWT аутентификацией, похожее на Trello.

## Возможности

- Регистрация и аутентификация пользователей (JWT)
- Управление пользователями (CRUD)
- Управление задачами (CRUD)
- Назначение задач пользователям
- Фильтрация задач по статусу, приоритету и ответственному
- Загрузка фотографий пользователей

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/trello-like-api.git
cd trello-like-api
```

2. Запуск проекта

```bash
uvicorn app.main:app --reload --port 8001

docker build -t my-app . --no-cache
docker run -d -p 8001:8001 --name my-app \-v $(pwd):/app \ app
docker logs -f my-app

```

3. Swagger
   http://127.0.0.1:8001/docs 

