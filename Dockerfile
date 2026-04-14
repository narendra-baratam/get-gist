# Stage 1: install dependencies
FROM python:3.12-alpine AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: lean runtime image
FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY app.py .

EXPOSE 8080

USER 1000:1000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
