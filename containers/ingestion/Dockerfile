FROM python:3.10-slim

WORKDIR /code
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./app /code/app
COPY ./assets /code/assets
COPY ./description.md /code/description.md

EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080