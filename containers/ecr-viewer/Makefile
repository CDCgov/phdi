.PHONY: help dev local-dev docker-compose-with-logs setup-local-env build start lint test test-watch convert-seed-data cypress-open cypress-run cypress-run-local cypress-run-prod

help:
	@echo "\033[1;32mAvailable commands:\033[0m"
	@echo "\033[1;36mmake dev\033[0m           \033[0;33m- Runs next dev\033[0m"
	@echo "\033[1;36mmake local-dev\033[0m    \033[0;33m- Runs npm run local-dev\033[0m"
	@echo "\033[1;36mmake docker-compose-with-logs\033[0m \033[0;33m- Runs docker compose up db -d && docker compose logs\033[0m"
	@echo "\033[1;36mmake setup-local-env\033[0m \033[0;33m- Runs setup-env.sh\033[0m"
	@echo "\033[1;36mmake build\033[0m        \033[0;33m- Runs next build\033[0m"
	@echo "\033[1;36mmake start\033[0m        \033[0;33m- Runs next start\033[0m"
	@echo "\033[1;36mmake lint\033[0m         \033[0;33m- Runs next lint\033[0m"
	@echo "\033[1;36mmake test\033[0m         \033[0;33m- Runs TZ=America/New_York jest\033[0m"
	@echo "\033[1;36mmake test-watch\033[0m   \033[0;33m- Runs TZ=America/New_York jest --watch\033[0m"
	@echo "\033[1;36mmake convert-seed-data\033[0m \033[0;33m- Runs docker compose -f ./seed-scripts/docker-compose.yml up --abort-on-container-exit\033[0m"
	@echo "\033[1;36mmake cypress-open\033[0m \033[0;33m- Opens Cypress\033[0m"
	@echo "\033[1;36mmake cypress-run\033[0m  \033[0;33m- Runs Cypress tests\033[0m"
	@echo "\033[1;36mmake cypress-run-local\033[0m  \033[0;33m- Runs Cypress tests in local environment\033[0m"
	@echo "\033[1;36mmake cypress-run-prod\033[0m  \033[0;33m- Runs Cypress tests in production environment\033[0m"
	@echo "\033[1;36mexit\033[0m              \033[0;33m- Exit\033[0m"
	@echo "\033[1;32mSelect a command to run:\033[0m"
	@select option in "dev" "local-dev" "docker-compose-with-logs" "setup-local-env" "build" "start" "lint" "test" "test-watch" "convert-seed-data" "cypress-open" "cypress-run" "cypress-run-local" "cypress-run-prod" "exit"; do \
		case $$option in \
			"dev") $(MAKE) dev;; \
			"local-dev") $(MAKE) local-dev;; \
			"docker-compose-with-logs") $(MAKE) docker-compose-with-logs;; \
			"setup-local-env") $(MAKE) setup-local-env;; \
			"build") $(MAKE) build;; \
			"start") $(MAKE) start;; \
			"lint") $(MAKE) lint;; \
			"test") $(MAKE) test;; \
			"test-watch") $(MAKE) test-watch;; \
			"convert-seed-data") $(MAKE) convert-seed-data;; \
			"cypress-open") $(MAKE) cypress-open;; \
			"cypress-run") $(MAKE) cypress-run;; \
			"cypress-run-local") $(MAKE) cypress-run-local;; \
			"cypress-run-prod") $(MAKE) cypress-run-prod;; \
			"exit") exit;; \
			*) echo "Invalid option. Please try again."; \
		esac; \
	done

dev:
	@echo "Running next dev..."
	npm run dev

local-dev:
	@echo "Running npm run local-dev..."
	npm run local-dev

docker-compose-with-logs:
	@echo "Running docker compose up db -d && docker compose logs..."
	npm run docker-compose-with-logs

setup-local-env:
	@echo "Setting up local environment..."
	npm run setup-local-env

build:
	@echo "Building the project..."
	npm run build

start:
	@echo "Starting the project..."
	npm run start

lint:
	@echo "Running lint..."
	npm run lint

test:
	@echo "Running tests..."
	npm run test

test-watch:
	@echo "Running tests in watch mode..."
	npm run test:watch

convert-seed-data:
	@echo "Running convert-seed-data..."
	npm run convert-seed-data

cypress-open:
	@echo "Opening Cypress..."
	npm run cypress:open

cypress-run:
	@echo "Running Cypress tests..."
	npm run cypress:run

cypress-run-local:
	@echo "Running Cypress tests in local environment..."
	npm run cypress:run-local

cypress-run-prod:
	@echo "Running Cypress tests in production environment..."
	npm run cypress:run-prod
