# Используем легкий образ Python
FROM python:3.12-slim

# отключает создание .pyc файлов.
ENV PYTHONDONTWRITEBYTECODE=1
#отключает буферизацию вывода stdout/stderr
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (если понадобятся для сборки psycopg2 и т.д.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY app .

CMD ["python", "-m", "app.main"]