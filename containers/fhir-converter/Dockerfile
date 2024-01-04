FROM mcr.microsoft.com/dotnet/sdk:3.1 as build

# Download FHIR-Converter
RUN git clone https://github.com/microsoft/FHIR-Converter.git --branch v5.0.4 --single-branch /build/FHIR-Converter
WORKDIR /build/FHIR-Converter
RUN echo test > src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/VXU_V04.liquid
RUN if [ -f src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/.wh.VXU_V04.liquid ]; then rm src/Microsoft.Health.Fhir.TemplateManagement.UnitTests/TestData/DecompressedFiles/.wh.VXU_V04.liquid; fi
RUN mkdir bin && \
  wget https://github.com/deislabs/oras/releases/download/v0.12.0/oras_0.12.0_windows_amd64.tar.gz -O ./bin/oras.tar.gz && \
  tar -xvf ./bin/oras.tar.gz -C ./bin

# Build Microsoft FHIR Converter
RUN dotnet build -c Release -o output

FROM mcr.microsoft.com/dotnet/runtime:3.1 as runtime

# Copy FHIR-Converter binary from build stage
COPY --from=build /build/FHIR-Converter/output /build/FHIR-Converter/output
COPY --from=build /build/FHIR-Converter/data/Templates /build/FHIR-Converter/data/Templates

ENV PYTHONUNBUFFERED=1

# Install python via pyenv
RUN apt-get update && apt-get install -y curl git build-essential libreadline-gplv2-dev  libncursesw5-dev  libssl-dev  libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
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
COPY description.md /code/description.md

# Copy eCR templates
COPY Templates/eCR /build/FHIR-Converter/data/Templates/eCR

EXPOSE 8080
CMD /root/.pyenv/shims/uvicorn app.main:app --host 0.0.0.0 --port 8080
