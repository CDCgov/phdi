.PHONY: help run-docker run-python build-image

help:
	@echo "\033[1;32mDIBBs Record Linkage Service Commands:\033[0m"
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
	@echo "Running Record Linkage service using Docker on localhost:8080..."
	docker pull ghcr.io/cdcgov/phdi/record-linkage:latest
	docker run -p 8080:8080 record-linkage:latest

run-python:
	@echo "Running Record Linkage service from Python source on localhost:8080..."
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

docker-local:
	$(MAKE) build-image && docker run -p 8080:8080 record-linkage

build-image:
	@echo "Building Docker image for the Record Linkage service..."
	docker buildx build --platform linux/amd64 -t record-linkage .
