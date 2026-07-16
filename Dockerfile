FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Копируем ВЕСЬ проект (включая src) ПЕРЕД установкой зависимостей
COPY . .

# Устанавливаем зависимости и сам пакет в режиме редактирования
RUN uv sync --no-dev

ENV PYTHONPATH=/app/src

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]