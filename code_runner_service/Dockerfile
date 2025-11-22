FROM python:3.11-slim

WORKDIR /app

# Обновляем систему и устанавливаем все необходимые компиляторы
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    time \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update && apt-get install -y \
    docker.io \
    build-essential \
    g++ \
    gcc \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["python", "app.py"]