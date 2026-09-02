FROM python:3.11-slim

WORKDIR /app

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌های پروژه
COPY manager_82.py .
COPY 78.py . 2>/dev/null || true

# نصب وابستگی‌های Python
RUN pip install --no-cache-dir telethon

# ایجاد دایرکتوری برای دیتابیس و کلاینت‌ها
RUN mkdir -p clients

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# اجرای ربات
CMD ["python", "-u", "manager_82.py"]
