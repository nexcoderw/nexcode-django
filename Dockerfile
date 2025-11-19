# Stage 1 — build
FROM python:3.11-slim AS builder

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies into isolated folder
COPY requirements.txt /app/
RUN python -m pip install --upgrade pip
RUN pip install --user -r requirements.txt

# Stage 2 — final
FROM python:3.11-slim

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# system deps required at runtime (pillow, libjpeg etc if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gcc \
    libjpeg62-turbo \
  && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy app code
COPY . /app

# Create a non-root user (optional but recommended)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Entrypoint & gunicorn
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=nexcode.settings
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["/entrypoint.sh"]
