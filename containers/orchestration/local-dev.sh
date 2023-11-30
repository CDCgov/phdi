# Validation
if docker ps | grep -q "validation"; then
    echo "Validation Container already running; skipping build and run"
elif docker ps -a | grep -q "validation"; then
    echo "Validation Container already built; running..."
    docker run -d -p 8081:8080 validation
else
    echo "validation Container does not exist, building and running..."
    # Build and run your Docker container here
    docker build --no-cache -t validation ../validation/ls
    docker run -d -p 8081:8080 validation
fi

# FHIR Converter
if docker ps | grep -q "fhir-converter"; then
    echo "fhir-converter Container already running; skipping build and run"
elif docker ps -a | grep -q "fhir-converter"; then
    echo "fhir-converter Container already built; running..."
    docker run -d -p 8082:8080 fhir-converter
else
    echo "fhir-converter Container does not exist, building and running..."
    # Build and run your Docker container here
    docker build --no-cache -t fhir-converter ../fhir-converter/
    docker run -d -p 8082:8080 fhir-converter
fi


# Message Parser
if docker ps | grep -q "message-parser"; then
    echo "message-parser Container already running; skipping build and run"
elif docker ps -a | grep -q "message-parser"; then
    echo "message-parser Container already built; running..."
    docker run -d -p 8085:8080 message-parser
else
    echo "message-parser Container does not exist, building and running..."
    # Build and run your Docker container here
    docker build --no-cache -t message-parser ../message-parser/
    docker run -d -p 8085:8080 message-parser
fi

# Ingestion
if docker ps | grep -q "ingestion"; then
    echo "ingestion Container already running; skipping build and run"
elif docker ps -a | grep -q "ingestion"; then
    echo "ingestion Container already built; running..."
    docker run -d -p 8083:8080 ingestion
else
    echo "ingestion Container does not exist, building and running..."
    # Build and run your Docker container here
    docker build --no-cache -t ingestion ../ingestion/
    docker run -d -p 8083:8080 ingestion
fi

# Orchestration
# docker build -t orchestration ./
# docker run -d -p 8080:8080 orchestration
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --env-file local-dev.env
