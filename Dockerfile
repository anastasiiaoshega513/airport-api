FROM python:3.12-slim
LABEL maintainer="anastasiaosega@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR /airport_service

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN chown -R django-user:django-user /airport_service

USER django-user
