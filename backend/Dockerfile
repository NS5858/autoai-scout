FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
RUN playwright install chromium

EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
