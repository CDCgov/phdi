#!/bin/bash

# Check if branch name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <branch-name>"
    exit 1
fi

BRANCH_NAME=$1

# Check if the value indicating whether to view the non-integrated viewer is provided/valid
if [ -n "$2" ]; then
    if [[ "$2" == "true" || "$2" == "false" ]]; then
        IS_NON_INTEGRATED=$2
    else
        echo "Invalid value for IS_NON_INTEGRATED. It must be 'true' or 'false'."
        exit 1
    fi
else
    IS_NON_INTEGRATED=true
fi

# Check if the value indicating whether to convert the seed data is provided/valid
if [ -n "$3" ]; then
    if [[ "$3" == "true" || "$3" == "false" ]]; then
        CONVERT_SEED_DATA=$3
    else
        echo "Invalid value for CONVERT_SEED_DATA. It must be 'true' or 'false'."
        exit 1
    fi
else
    CONVERT_SEED_DATA=false
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install Homebrew if it's not already installed
if ! command_exists brew; then
    echo "Homebrew not found, installing it now..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Update Homebrew
brew update

# Install Git if it's not already installed
if ! command_exists git; then
    brew install git
fi

# Install Docker if it's not already installed
if ! command_exists docker; then
    brew install --cask docker
fi

# Start Docker
open /Applications/Docker.app
echo "Waiting for Docker to launch..."
while ! docker system info > /dev/null 2>&1; do
    sleep 1
done

# Clone the repository if it doesn't exist, otherwise pull the latest changes
REPO_URL="https://github.com/CDCgov/phdi.git"
REPO_DIR="phdi"

if [ ! -d "$REPO_DIR" ]; then
    git clone $REPO_URL
    cd $REPO_DIR
else
    cd $REPO_DIR
    git pull
fi

cd ./containers/ecr-viewer

# Checkout the specified branch
git checkout $BRANCH_NAME

# Write env vars to .env.local
echo "APP_ENV=test" > .env.local
echo "DATABASE_URL=postgres://postgres:pw@db:5432/ecr_viewer_db" >> .env.local
echo "NEXT_PUBLIC_NON_INTEGRATED_VIEWER=$IS_NON_INTEGRATED" >> .env.local

# Run FHIR conversion on seed data
if [ "$CONVERT_SEED_DATA" = true ]; then
  echo "Running seed data FHIR conversion..."

  docker compose -f ./seed-scripts/docker-compose.yml --profile design-review down -v
  docker compose -f ./seed-scripts/docker-compose.yml --profile seed-postgres --env-file .env.local up --abort-on-container-exit
else
  echo "Skipping seed data FHIR conversion..."
fi

# Build and run docker compose
docker compose -f ./seed-scripts/docker-compose.yml --profile design-review --env-file .env.local up -d --build

# Wait for eCR Viewer to be available
URL="http://localhost:3000/ecr-viewer"
while ! curl -s -o /dev/null -w "%{http_code}" "$URL" | grep -q "200"; do
    echo "Waiting for $URL to be available..."
    sleep 5
done

# Open in default browser
open http://localhost:3000/ecr-viewer

# Prompt to end review session
read -p "Press enter to end review"
docker compose -f ./seed-scripts/docker-compose.yml --profile design-review down
docker compose -f ./seed-scripts/docker-compose.yml --profile seed-postgres down