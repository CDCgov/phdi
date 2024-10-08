#!/bin/bash

# Check if .env.local exists
if [ ! -f .env.local ]; then
    # If .env.local doesn't exist, copy .env to .env.local
    cp .env .env.local
    echo ".env.local was created from .env"
else
    echo ".env.local already exists"
fi

