FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file
COPY ./requirements.txt /code/requirements.txt

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the container
COPY create-seed-data.py /code/create-seed-data.py
COPY ./baseECR /code/baseECR
ENV PYTHONUNBUFFERED=1

# Command to run the script
CMD ["python", "./create-seed-data.py"]