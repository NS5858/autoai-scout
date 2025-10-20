FROM python:3.10-slim
WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
COPY . .
ENV PORT=10000
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
