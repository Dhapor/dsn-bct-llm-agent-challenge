FROM python:3.11-slim

WORKDIR /app

COPY task_a/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY shared /app/shared
COPY task_a /app/task_a

WORKDIR /app/task_a

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}"]
