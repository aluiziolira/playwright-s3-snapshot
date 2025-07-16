.PHONY: test test-verbose test-coverage install-dev clean lint format help

# Default target
help:
	@echo "Available targets:"
	@echo "  install-dev    Install development dependencies"
	@echo "  test           Run tests with coverage"
	@echo "  test-verbose   Run tests with verbose output"
	@echo "  test-coverage  Run tests and open coverage report"
	@echo "  lint           Run code linting"
	@echo "  format         Format code with black"
	@echo "  clean          Clean up generated files"

# Install development dependencies
install-dev:
	pip install -e .[dev]

# Run tests with coverage (minimum 90%)
test:
	pytest --cov=src/playwright_s3_snapshot --cov-report=html --cov-report=term-missing --cov-fail-under=90

# Run tests with verbose output
test-verbose:
	pytest --cov=src/playwright_s3_snapshot --cov-report=html --cov-report=term-missing --cov-fail-under=90 -v

# Run tests and open coverage report
test-coverage: test
	@echo "Opening coverage report..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open > /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo "Coverage report available at htmlcov/index.html"; \
	fi

# Run linting
lint:
	ruff check src/ tests/
	black --check src/ tests/

# Format code
format:
	black src/ tests/
	ruff check --fix src/ tests/

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete