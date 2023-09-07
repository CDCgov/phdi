# Validation
if docker ps -a | grep -q "validation"; then
    echo "Container exists, skipping build and run"
else
    echo "Container does not exist, building and running..."
    # Build and run your Docker container here
    docker build --no-cache -t validation ../validation/
    docker run -d -p 8081:8080 validation
fi

# Orchestration
# docker build -t orchestration ./
# docker run -d -p 8080:8080 orchestration
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
