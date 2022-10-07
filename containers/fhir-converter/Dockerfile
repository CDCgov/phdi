FROM python:3.10

# Install dotnet
RUN curl -sSL https://dot.net/v1/dotnet-install.sh | \
    bash /dev/stdin -Channel 3.1 -InstallDir /usr/share/dotnet && \
    ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet

# Download FHIR-Converter
WORKDIR /build
RUN git clone https://github.com/microsoft/FHIR-Converter.git --branch v5.0.4 --single-branch
WORKDIR /build/FHIR-Converter

# Build Microsoft FHIR Converter binary. Need to run twice due to strange error copying oras.exe
RUN dotnet build || true
RUN dotnet build

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

EXPOSE 8080
CMD uvicorn main:api --host 0.0.0.0 --port 8080