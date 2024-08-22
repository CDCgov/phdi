.PHONY: help run-docker run-python build-image

# Load configuration files
include ../config.env
-include ../local-config.env

help:
	@echo "\033[1;32mDIBBs Trigger Code Reference Service Commands:\033[0m"
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
	@echo "Running Trigger Code Reference service using Docker on localhost:$(TRIGGER_CODE_REFERENCE_PORT)..."
	docker pull ghcr.io/cdcgov/phdi/trigger-code-reference:latest
	docker run -p $(TRIGGER_CODE_REFERENCE_PORT):8080 trigger-code-reference:latest

run-python:
	@echo "Running Trigger Code Reference service from Python source on localhost:$(TRIGGER_CODE_REFERENCE_PORT)..."
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port $(TRIGGER_CODE_REFERENCE_PORT)

docker-local:
	$(MAKE) build-image && docker run -p $(TRIGGER_CODE_REFERENCE_PORT):8080 trigger-code-reference

build-image:
	@echo "Building Docker image for the Trigger Code Reference service..."
	docker buildx build --platform linux/amd64 -t trigger-code-reference .
