# Используем легкий образ Python
FROM python:3.12-slim

# Отключает создание .pyc файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей ИЗ папки backend
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения (из backend/app в /app контейнера)
COPY backend/app ./app

# ЗАПУСК: используем uvicorn с --reload для разработки
# Это позволит видеть изменения в коде без пересборки контейнера
CMD ["python", "-m", "app.main"]