FROM ghcr.io/cdcgov/phdi/dibbs

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./app /code/app
COPY ./assets /code/assets
COPY ./seed-scripts /code/seed-scripts
COPY ./description.md /code/description.md

EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080