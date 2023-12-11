FROM python:3.10

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file
COPY requirements.txt ./

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the container
COPY seed-database.py .
COPY ./fhir_data .

# Command to run the script
CMD ["python", "./seed-database.py"]