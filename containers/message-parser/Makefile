.PHONY: help run-docker run-python build-image

# Load configuration files
include ../config.env
-include ../local-config.env

help:
	@echo "\033[1;32mDIBBs Message Parser Service Commands:\033[0m"
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
	@echo "Running Message Parser service using Docker on localhost:$(MESSAGE_PARSER_PORT)..."
	docker pull ghcr.io/cdcgov/phdi/message-parser:latest
	docker run -p $(MESSAGE_PARSER_PORT):8080 message-parser:latest

run-python:
	@echo "Running Message Parser service from Python source on localhost:$(MESSAGE_PARSER_PORT)..."
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt && \
	python -m uvicorn app.main:app --host 0.0.0.0 --port $(MESSAGE_PARSER_PORT)

docker-local:
	$(MAKE) build-image && docker run -p $(MESSAGE_PARSER_PORT):8080 message-parser

build-image:
	@echo "Building Docker image for the Message Parser service..."
	docker buildx build --platform linux/amd64 -t message-parser .
