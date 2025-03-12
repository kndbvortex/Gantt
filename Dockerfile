FROM python:3.10-slim AS builder

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

RUN pip install --upgrade pip 

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.10-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

USER appuser

RUN python manage.py collectstatic --noinput

EXPOSE 8001 

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "3", "gantt.wsgi:application"]
