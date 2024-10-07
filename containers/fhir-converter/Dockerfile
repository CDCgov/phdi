FROM mcr.microsoft.com/dotnet/sdk:6.0 as build

# Download FHIR-Converter
RUN git clone https://github.com/skylight-hq/FHIR-Converter.git --branch main --single-branch /build/FHIR-Converter
COPY /CustomFhir/CustomFilters.cs /build/FHIR-Converter/src/Microsoft.Health.Fhir.Liquid.Converter/Filters/

WORKDIR /build/FHIR-Converter

RUN pwd && ls -la

RUN echo test > src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/VXU_V04.liquid
RUN if [ -f src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/.wh.VXU_V04.liquid ]; then rm src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/.wh.VXU_V04.liquid; fi
RUN mkdir bin && \
  wget https://github.com/deislabs/oras/releases/download/v0.12.0/oras_0.12.0_windows_amd64.tar.gz -O ./bin/oras.tar.gz && \
  tar -xvf ./bin/oras.tar.gz -C ./bin

# Build Microsoft FHIR Converter
RUN dotnet build -c Release -o output

FROM mcr.microsoft.com/dotnet/runtime:6.0 as runtime

# Copy FHIR-Converter binary from build stage
COPY --from=build /build/FHIR-Converter/output /build/FHIR-Converter/output
COPY --from=build /build/FHIR-Converter/data/Templates /build/FHIR-Converter/data/Templates

ENV PYTHONUNBUFFERED=1

# Install python via pyenv
RUN apt-get update && apt-get install -y curl git build-essential libreadline-dev libncursesw5-dev  libssl-dev  libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
RUN curl https://pyenv.run | bash
RUN export PYENV_ROOT="$HOME/.pyenv"
RUN export PATH="$PYENV_ROOT/bin:$PATH"
RUN eval "$(pyenv init -)"
RUN /root/.pyenv/bin/pyenv install 3.10.13
RUN /root/.pyenv/bin/pyenv global 3.10.13

RUN /root/.pyenv/shims/pip install --no-cache --upgrade pip setuptools

# Install requirements
WORKDIR /code
COPY requirements.txt .
RUN /root/.pyenv/shims/pip install -r requirements.txt

# Copy FastAPI app
COPY app /code/app
COPY assets /code/assets
COPY README.md /code/README.md
COPY /CustomFhir/Loinc.csv /code/

# Copy eCR templates
COPY Templates/eCR /build/FHIR-Converter/data/Templates/eCR

# Copy ELR template to the Hl7v2 folder
COPY Templates/ELR/ELR.liquid /build/FHIR-Converter/data/Templates/Hl7v2

EXPOSE 8080
CMD /root/.pyenv/shims/uvicorn app.main:app --host 0.0.0.0 --port 8080
