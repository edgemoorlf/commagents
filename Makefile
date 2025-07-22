# AI Avatar Platform - Development Makefile

.PHONY: help install test lint format clean setup docs

# Default target
help:
	@echo "AI Avatar Platform - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  make install     Install package and dependencies"
	@echo "  make setup       Full development setup (dirs, config, etc.)"
	@echo ""
	@echo "Development:"
	@echo "  make test        Run all tests"
	@echo "  make test-infra  Test infrastructure only"
	@echo "  make lint        Run linters (flake8, mypy)"
	@echo "  make format      Format code with black"
	@echo "  make check       Run lint + format check"
	@echo ""
	@echo "Running:"
	@echo "  make run         Run platform in full mode"
	@echo "  make run-avatar  Run platform in avatar mode"
	@echo "  make example     Run football commentary example"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       Clean build artifacts"
	@echo "  make clean-logs  Clean log files"
	@echo ""

# Installation and setup
install:
	pip install -e ".[dev]"

setup: install
	@echo "🔧 Setting up development environment..."
	mkdir -p logs data
	@if [ ! -f config/config2.yaml ]; then \
		cp config/config2.example.yaml config/config2.yaml; \
		echo "📋 Copied configuration template to config/config2.yaml"; \
		echo "⚠️  Please update API keys in config/config2.yaml"; \
	fi
	@echo "✅ Setup complete!"

# Testing
test:
	pytest -v

test-infra:
	python test_infrastructure.py

# Code quality
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
	mypy core/ workflows/ tools/ utils/ --ignore-missing-imports

format:
	black --line-length 100 .

format-check:
	black --check --line-length 100 .

check: format-check lint
	@echo "✅ Code quality checks passed!"

# Running applications
run:
	python main.py --mode full

run-avatar:
	python main.py --mode avatar

run-content:
	python main.py --mode content

example:
	python agents/football_commentary_team.py

# Maintenance
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

clean-logs:
	rm -rf logs/*

# Development helpers
requirements:
	pip freeze > requirements-frozen.txt

env-info:
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Current directory: $(shell pwd)"
	@echo "Virtual environment: $(VIRTUAL_ENV)"

# Install pre-commit hooks (optional)
hooks:
	pip install pre-commit
	pre-commit install