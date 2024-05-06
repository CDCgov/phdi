FROM python:3.11-slim

RUN apt-get update && \
    apt-get upgrade -y

RUN pip install --upgrade pip

COPY . /dibbs
RUN pip install /dibbs