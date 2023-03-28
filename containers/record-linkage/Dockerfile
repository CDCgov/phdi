FROM python:3.10.10
# FROM python:3.10-slim-buster

WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git 
    # && \
    # apt-get -y install sudo && \
    # apt-get install -y libpq5=11.19-0+deb10u1 && \
    # apt-get install -y libpq-dev python-dev

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./app /code/app
COPY ./description.md /code/description.md
COPY ./migrations /code/migrations

EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080