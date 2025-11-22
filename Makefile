# Makefile for Data Analytics Pipeline

.PHONY: help install install-dev test lint format clean generate-data setup

# Default target
help:
	@echo "Data Analytics Pipeline - Available Commands:"
	@echo ""
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make lint             Run all linters"
	@echo "  make format           Format code with black and isort"
	@echo "  make generate-data    Generate sample data files"
	@echo "  make clean            Clean generated files and caches"
	@echo "  make setup            Complete setup (install + generate data)"
	@echo ""

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run all tests
test:
	pytest tests/ -v --cov=src --cov-report=term-missing

# Run unit tests only
test-unit:
	pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Run all linters
lint:
	@echo "Running black..."
	black --check src/ tests/
	@echo "Running flake8..."
	flake8 src/ tests/
	@echo "Running pylint..."
	pylint src/ --fail-under=8.0 || true
	@echo "Running mypy..."
	mypy src/ --ignore-missing-imports || true

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Generate sample data
generate-data:
	@echo "Generating sample data..."
	python src/data-generators/generate_transactions.py --rows 10000 --output data/transactions.csv
	python src/data-generators/generate_products.py --rows 500 --output data/products.json
	python src/data-generators/generate_clickstream.py --rows 5000 --output data/clickstream.json
	python src/data-generators/generate_reviews.py --rows 1000 --output data/reviews.csv
	@echo "Sample data generated successfully!"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	rm -rf data/*.csv data/*.json 2>/dev/null || true
	@echo "Cleanup complete!"

# Complete setup
setup: install-dev generate-data
	@echo "Setup complete! Run 'make test' to verify."

# Terraform commands
tf-init:
	cd terraform/environments/dev && terraform init

tf-plan:
	cd terraform/environments/dev && terraform plan

tf-apply:
	cd terraform/environments/dev && terraform apply

tf-destroy:
	cd terraform/environments/dev && terraform destroy

# Docker commands (for LocalStack testing)
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Documentation
docs:
	@echo "Documentation available in docs/ directory:"
	@echo "  - README.md - Project overview"
	@echo "  - ARCHITECTURE.md - Architecture details"
	@echo "  - DATA_DICTIONARY.md - Schema documentation"
	@echo "  - PROJECT_STATUS.md - Implementation status"
