FROM python:3.7-slim

WORKDIR /app_backend

COPY ../requirements.txt /app_backend/

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app_backend/

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]
