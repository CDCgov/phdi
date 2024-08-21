.PHONY: help dev dev-win setup-local-env build start lint test test-unit test-unit-watch test-integration cypress-open cypress-run

help:
	@echo "\033[1;32mTEFCA Viewer Commands:\033[0m"
	@select option in "dev" "dev-win" "setup-local-env" "build" "start" "lint" "test" "test-unit" "test-unit-watch" "test-integration" "cypress-open" "cypress-run" "exit"; do \
		case $$option in \
			"dev") $(MAKE) dev; break;; \
			"dev-win") $(MAKE) dev-win; break;; \
			"setup-local-env") $(MAKE) setup-local-env; break;; \
			"build") $(MAKE) build; break;; \
			"start") $(MAKE) start; break;; \
			"lint") $(MAKE) lint; break;; \
			"test") $(MAKE) test; break;; \
			"test-unit") $(MAKE) test-unit; break;; \
			"test-unit-watch") $(MAKE) test-unit-watch; break;; \
			"test-integration") $(MAKE) test-integration; break;; \
			"cypress-open") $(MAKE) cypress-open; break;; \
			"cypress-run") $(MAKE) cypress-run; break;; \
			"exit") echo "Exiting..."; break;; \
			*) echo "Invalid option. Please try again."; \
		esac; \
	done

dev:
	@echo "Running development environment with NODE_TLS_REJECT_UNAUTHORIZED=0..."
	npm run dev

dev-win:
	@echo "Running development environment for Windows..."
	npm run dev-win

setup-local-env:
	@echo "Setting up local environment..."
	npm run setup-local-env

build:
	@echo "Building project..."
	npm run build

start:
	@echo "Starting the project with NODE_TLS_REJECT_UNAUTHORIZED=0..."
	npm run start

lint:
	@echo "Running lint..."
	npm run lint

test:
	@echo "Running all tests (unit and integration)..."
	npm run test

test-unit:
	@echo "Running unit tests..."
	npm run test:unit

test-unit-watch:
	@echo "Running unit tests in watch mode..."
	npm run test:unit:watch

test-integration:
	@echo "Running integration tests..."
	npm run test:integration

cypress-open:
	@echo "Opening Cypress..."
	npm run cypress:open

cypress-run:
	@echo "Running Cypress tests..."
	npm run cypress:run
