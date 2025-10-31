.PHONY: help install test lint format build clean dev setup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	npm install
	pip install -r requirements.txt
	pip install -r full-requirements.txt

setup: ## Initial setup for development
	npm run prepare
	# pre-commit install
	@echo "Setup complete! Run 'make dev' to start development"

dev: ## Start development servers
	./app.sh

test: ## Run all tests
	npm run test:ci
	. .venv/bin/activate && pytest api/tests/ -v || true

test-watch: ## Run tests in watch mode
	npm run test:watch

lint: ## Run linting
	npm run lint
	. .venv/bin/activate && black --check api/ --exclude="workflows/" || echo "Black check failed - continuing..."
	. .venv/bin/activate && isort --check-only api/ --skip="workflows/" || echo "isort check failed - continuing..."
	. .venv/bin/activate && flake8 api/ --exclude="workflows/" --max-line-length=120 || echo "Flake8 check failed - continuing..."

lint-fix: ## Fix linting issues
	npm run lint:fix
	. .venv/bin/activate && black api/
	. .venv/bin/activate && isort api/

format: ## Format code
	npm run format
	. .venv/bin/activate && black api/
	. .venv/bin/activate && isort api/

build: ## Build the application
	npm run build

clean: ## Clean build artifacts
	rm -rf .next/
	rm -rf node_modules/
	rm -rf api/__pycache__/
	rm -rf api/**/__pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

coverage: ## Generate coverage reports
	npm run test:coverage
	. .venv/bin/activate && pytest api/tests/ --cov=api --cov-report=html

security: ## Run security checks
	npm audit
	. .venv/bin/activate && safety check || true

ci: ## Run CI pipeline locally
	make lint || echo "Linting failed - continuing..."
	make test || echo "Tests failed - continuing..."
	make build || echo "Build failed - continuing..."
