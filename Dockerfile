# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /my_app
COPY ./app/requirements.txt /my_app/
RUN pip install -r requirements.txt
COPY . /my_app/
