FROM python:3.10-slim-buster

WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./app /code/app

EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080