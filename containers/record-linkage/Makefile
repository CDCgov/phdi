.PHONY: help run-docker run-python build-image

# Load configuration files
include ../config.env
-include ../local-config.env

help:
	@echo "\033[1;32mDIBBs Record Linkage Service Commands:\033[0m"
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
	@echo "Running Record Linkage service using Docker on localhost:$(RECORD_LINKAGE_PORT)..."
	docker pull ghcr.io/cdcgov/phdi/record-linkage:latest
	docker run -p $(RECORD_LINKAGE_PORT):8080 record-linkage:latest

run-python:
	@echo "Running Record Linkage service from Python source on localhost:$(RECORD_LINKAGE_PORT)..."
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port $(RECORD_LINKAGE_PORT)

docker-local:
	$(MAKE) build-image && docker run -p $(RECORD_LINKAGE_PORT):8080 record-linkage

build-image:
	@echo "Building Docker image for the Record Linkage service..."
	docker buildx build --platform linux/amd64 -t record-linkage .
