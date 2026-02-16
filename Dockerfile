FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev curl

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# create non-root user
RUN useradd --create-home appuser
RUN chown -R appuser /app
USER appuser

ENV FLASK_APP=manage.py

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "manage:app", "--workers", "3", "--worker-class", "gthread", "--threads", "2", "--timeout", "120"]
