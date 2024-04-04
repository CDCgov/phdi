FROM python:3.10

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file
COPY ./requirements.txt /code/requirements.txt

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the container
COPY seed-database.py /code/seed-database.py
COPY ./fhir_data /code/fhir_data

# Command to run the script
CMD ["python", "./seed-database.py"]