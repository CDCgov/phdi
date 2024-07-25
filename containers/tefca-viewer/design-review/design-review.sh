#!/bin/bash

# Check if branch name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <branch-name>"
    exit 1
fi

BRANCH_NAME=$1

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

# Install Docker Compose if it's not already installed
if ! command_exists docker-compose; then
    brew install docker-compose
fi

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

cd ./containers/tefca-viewer

# Checkout the specified branch
git checkout $BRANCH_NAME

# Build and run docker-compose
docker-compose build --no-cache && docker-compose up -d

# Wait for TEFCA Viewer to be available
URL="http://localhost:3000/tefca-viewer"
while ! curl -s -o /dev/null -w "%{http_code}" "$URL" | grep -q "200"; do
    echo "Waiting for $URL to be available..."
    sleep 5
done


# Open in default browser
open http://localhost:3000/tefca-viewer

# Prompt to end review session
read -p "Press enter to end review"
docker compose down
