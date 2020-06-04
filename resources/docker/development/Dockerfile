## base image
FROM python:3.7.5-slim-buster

## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean


## set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## set working directory
WORKDIR /usr/src/app

## add and install requirements
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt


# copy entrypoint.sh
COPY ./resources/docker/development/entrypoint.sh /usr/src/app/resources/docker/development/entrypoint.sh

## add app
COPY . /usr/src/app

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/resources/docker/development/entrypoint.sh"]

## run server
CMD python manage.py runserver 0.0.0.0:8000