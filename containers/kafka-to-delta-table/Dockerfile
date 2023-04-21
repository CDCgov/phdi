FROM python:3.10-slim-bullseye

WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git wget procps gcc

RUN apt-get install -y gnupg ca-certificates software-properties-common  openjdk-17-jdk openjdk-17-jre -y

# Add Java binaries to the system path
ENV PATH $JAVA_HOME/bin:$PATH

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.2/hadoop-common-3.3.2.jar  -o /usr/local/lib/python3.10/site-packages/pyspark/jars/hadoop-common-3.3.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure/3.3.2/hadoop-azure-3.3.2.jar    -o /usr/local/lib/python3.10/site-packages/pyspark/jars/hadoop-azure-3.3.2.jar
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure-datalake/3.3.2/hadoop-azure-datalake-3.3.2.jar -o /usr/local/lib/python3.10/site-packages/pyspark/jars/hadoop-azure-datalake-3.3.2.jar 
RUN wget https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
RUN tar -xvzf spark-3.3.2-bin-hadoop3.tgz
RUN mv spark-3.3.2-bin-hadoop3 /usr/local/spark

COPY ./app /code/app
COPY ./kafka_to_delta.py /code/kafka_to_delta.py
COPY ./description.md /code/description.md

EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080