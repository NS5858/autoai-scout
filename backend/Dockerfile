FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Systempakete installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis im Container
WORKDIR /app

# Anforderungen installieren
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# App-Code kopieren
COPY ./app ./app

# Port freigeben
EXPOSE 8000

# Startbefehl (korrekt für Render & Ordnerstruktur)
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000", "--app-dir", "app"]
