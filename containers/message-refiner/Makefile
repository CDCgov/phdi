.PHONY: help run-docker run-python build-image

# Load configuration files
include ../config.env
-include ../local-config.env

help:
	@echo "\033[1;32mDIBBs Message Refiner Service Commands:\033[0m"
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
	@echo "Running Message Refiner service using Docker on localhost:$(MESSAGE_REFINER_PORT)..."
	docker pull ghcr.io/cdcgov/phdi/message-refiner:latest
	docker run -p $(MESSAGE_REFINER_PORT):8080 message-refiner:latest

run-python:
	@echo "Running Message Refiner service from Python source on localhost:$(MESSAGE_REFINER_PORT)..."
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port $(MESSAGE_REFINER_PORT)

docker-local:
	$(MAKE) build-image && docker run -p $(MESSAGE_REFINER_PORT):8080 message
