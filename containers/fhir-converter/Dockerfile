FROM mcr.microsoft.com/dotnet/sdk:3.1 as build

# Download FHIR-Converter
RUN git clone https://github.com/microsoft/FHIR-Converter.git --branch v5.0.4 --single-branch /build/FHIR-Converter
WORKDIR /build/FHIR-Converter
RUN echo test > src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/VXU_V04.liquid
RUN rm src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/.wh.VXU_V04.liquid
RUN mkdir bin && \
    wget https://github.com/deislabs/oras/releases/download/v0.12.0/oras_0.12.0_windows_amd64.tar.gz -O ./bin/oras.tar.gz && \
    tar -xvf ./bin/oras.tar.gz -C ./bin

# Build Microsoft FHIR Converter
RUN dotnet build -c Release -o output

FROM mcr.microsoft.com/dotnet/runtime:3.1 as runtime

# Copy FHIR-Converter binary from build stage
COPY --from=build /build/FHIR-Converter/output /build/FHIR-Converter/output
COPY --from=build /build/FHIR-Converter/data/Templates /build/FHIR-Converter/data/Templates

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install --no-cache --upgrade pip setuptools

# Install requirements
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy FastAPI app
COPY app/main.py .

# Copy eCR templates
COPY Templates/eCR /build/FHIR-Converter/data/Templates/eCR

EXPOSE 8080
CMD uvicorn main:app --host 0.0.0.0 --port 8080