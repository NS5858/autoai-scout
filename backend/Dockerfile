# ---- Basis-Image: Python + Playwright ----
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# ---- Arbeitsverzeichnis ----
WORKDIR /app/backend

# ---- Dependencies installieren ----
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    playwright install chromium

# ---- Projektdateien kopieren ----
COPY . .

# ---- Port setzen ----
ENV PORT=10000
EXPOSE 10000

# ---- FastAPI starten ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
