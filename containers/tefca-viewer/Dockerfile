FROM python:3.10-slim

ARG MESSAGE_PARSER_URL

WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./app /code/app
COPY ./description.md /code/description.md

ENV MESSAGE_PARSER_URL=$MESSAGE_PARSER_URL

EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080