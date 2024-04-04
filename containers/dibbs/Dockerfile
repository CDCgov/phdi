FROM python:3.10-slim

RUN apt-get update && \
    apt-get upgrade -y

COPY . /dibbs
RUN pip install /dibbs