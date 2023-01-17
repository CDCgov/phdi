FROM python:3.10-slim-buster

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./main.py /code/main.py
COPY ./description.md /code/description.md

EXPOSE 8080
CMD uvicorn main:api --host 0.0.0.0 --port 8080