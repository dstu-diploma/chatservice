# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Final image
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY app app
COPY migrations migrations
COPY aerich.ini aerich.ini
COPY pyproject.toml pyproject.toml

COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 8000
ENV PYTHONPATH=/app

ENTRYPOINT ["./entrypoint.sh"]
