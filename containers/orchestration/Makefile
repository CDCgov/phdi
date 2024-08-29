.PHONY: help run-docker run-python build-image dev local-dev support-services docker-local

help:
	@echo "\033[1;32mDIBBs Orchestration Commands:\033[0m"
	@select option in "run-docker" "run-python" "build-image" "docker-local" "local-dev" "support-services" "exit"; do \
		case $$option in \
			"run-docker") $(MAKE) run-docker; break;; \
			"run-python") $(MAKE) run-python; break;; \
			"build-image") $(MAKE) build-image; break;; \
			"docker-local") $(MAKE) docker-local; break;; \
			"local-dev") $(MAKE) local-dev; break;; \
			"support-services") $(MAKE) support-services; break;; \
			"exit") echo "Exiting..."; break;; \
			*) echo "Invalid option. Please try again."; \
		esac; \
	done

run-docker:
	@echo "Running Orchestration using Docker on localhost:8080..."
	docker pull ghcr.io/cdcgov/phdi/orchestration:latest
	docker run -p 8080:8080 orchestration:latest

run-python:
	@echo "Running Orchestration from Python source on localhost:8080..."
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --env-file local-dev.env

docker-local:
	$(MAKE) build-image && docker run -p 8080:8080 orchestration

build-image:
	@echo "Building Docker image for the Orchestration..."
	docker buildx build --platform linux/amd64 -t orchestration .

local-dev:
	@echo "Starting local development environment..."
	$(MAKE) support-services && export DATABASE_URL=postgresql://postgres:pw@localhost:5432/ecr_viewer_db && $(MAKE) run-python

support-services:
	@echo "Starting support services..."
	docker compose up ecr-viewer-db ecr-viewer validation-service fhir-converter-service ingestion-service trigger-code-reference-service message-parser-service -d && docker compose logs
