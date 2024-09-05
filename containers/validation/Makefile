.PHONY: help run-docker run-python build-image

# Load configuration file
include ../config.env
-include ../local-config.env

help:
	@echo "\033[1;32mDIBBs Validation Service Commands:\033[0m"
	@select option in "run-docker" "run-python" "build-image" "docker-local" "exit"; do \
		case $$option in \
			"run-docker") $(MAKE) run-docker; break;; \
			"run-python") $(MAKE) run-python; break;; \
			"build-image") $(MAKE) build-image; break;; \
			"docker-local") $(MAKE) docker-local; break;;\
			"exit") echo "Exiting..."; break;; \
			*) echo "Invalid option. Please try again."; \
		esac; \
	done

run-docker:
	@echo "Running Validation service using Docker on localhost:$(VALIDATION_PORT)..."
	docker pull ghcr.io/cdcgov/phdi/validation:latest
	docker run -p $(VALIDATION_PORT):8080 validation:latest

run-python:
	@echo "Running Validation service from Python source on localhost:$(VALIDATION_PORT)..."
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port $(VALIDATION_PORT)

docker-local:
	@echo "Building docker container and running on localhost:$(VALIDATION_PORT)..."
	$(MAKE) build-image && docker run -p $(VALIDATION_PORT):8080 validation

build-image:
	@echo "Building Docker image for the Validation service..."
	docker buildx build --platform linux/amd64 -t validation .
