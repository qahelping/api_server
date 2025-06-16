FROM python:3.12-slim

WORKDIR /app

# Копируем только зависимости сначала для кэширования
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем uvicorn (если его нет в requirements.txt)
RUN pip install uvicorn

EXPOSE 8001

# Запускаем с reload для отслеживания изменений
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]