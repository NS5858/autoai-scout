# Playwright + Python + alle Browser-Dependencies fix & gepflegt
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

# zuerst nur Requirements kopieren, damit Docker-Cache wirkt
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# dann den restlichen Code
COPY . .

# Render erwartet einen offenen Port
ENV PORT=10000
EXPOSE 10000

# FastAPI starten (liegt bei dir als backend/main.py)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]

