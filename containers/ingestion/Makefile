.PHONY: help run-docker run-python build-image

# Load configuration files
include ../config.env
-include ../local-config.env

help:
	@echo "\033[1;32mDIBBs Ingestion Service Commands:\033[0m"
	@select option in "run-docker" "run-python" "build-image" "docker-local" "exit"; do \
		case $$option in \
			"run-docker") $(MAKE) run-docker; break;; \
			"run-python") $(MAKE) run-python; break;; \
			"build-image") $(MAKE) build-image; break;; \
			"docker-local") $(MAKE) docker-local; break;; \
			"exit") echo "Exiting..."; break;; \
			*) echo "Invalid option. Please try again."; \
		esac; \
	done

run-docker:
	@echo "Running Ingestion service using Docker on localhost:$(INGESTION_PORT)..."
	docker pull ghcr.io/cdcgov/phdi/ingestion:latest
	docker run -p $(INGESTION_PORT):8080 ingestion:latest

run-python:
	@echo "Running Ingestion service from Python source on localhost:$(INGESTION_PORT)..."
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port $(INGESTION_PORT)

docker-local:
	$(MAKE) build-image && docker run -p $(INGESTION_PORT):8080 ingestion

build-image:
	@echo "Building Docker image for the Ingestion service..."
	docker buildx build --platform linux/amd64 -t ingestion .
