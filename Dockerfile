# ====================
# Builder stage
# ====================
FROM python:3.11-slim AS builder

WORKDIR /app

# System build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN python -m pip install --upgrade pip
RUN pip install --user -r requirements.txt


# ====================
# Final stage
# ====================
FROM python:3.11-slim

WORKDIR /app

# Runtime packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gcc \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# --- FIX IS HERE ---
# Copy entrypoint WHILE STILL ROOT
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# --------------------

# Copy python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Add project source code
COPY . /app

# Create non-root user AFTER entrypoint is already copied
RUN useradd -m appuser && chown -R appuser:appuser /app

ENV PATH=/root/.local/bin:$PATH
ENV DJANGO_SETTINGS_MODULE=nexcode.settings

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
