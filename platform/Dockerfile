# PureData - AI训练数据生成平台
FROM python:3.11-slim

LABEL maintainer="PureData Team"
LABEL version="2.0.0"
LABEL description="AI Training Data Generation Platform"

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

RUN mkdir -p /app/backend/data /app/backend/logs /app/backend/cache /app/backend/outputs /app/backend/keywords /app/backend/domain_configs /app/backend/domain_templates

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "backend/simple_main.py"]
