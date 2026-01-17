.PHONY: help install local test docker-build docker-run deploy destroy clean

help:
	@echo "RAG Student Support - Makefile Commands"
	@echo ""
	@echo "Local Development:"
	@echo "  make install      - Install dependencies"
	@echo "  make local        - Run locally (local mode)"
	@echo "  make test         - Run tests"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with docker-compose"
	@echo ""
	@echo "Azure:"
	@echo "  make deploy       - Deploy to Azure (requires --subscription and --resource-group)"
	@echo "  make destroy      - Destroy Azure resources (requires --resource-group)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean Python cache files"

install:
	pip install -r requirements.txt

local:
	@if [ ! -f .env ]; then \
		cp .env.local.example .env; \
		echo "Created .env file from template"; \
	fi
	python -m app.main

test:
	python -m pytest tests/ -v

docker-build:
	docker build -t rag-student-support:latest .

docker-run:
	docker-compose up --build

deploy:
	@if [ -z "$(SUBSCRIPTION)" ] || [ -z "$(RESOURCE_GROUP)" ]; then \
		echo "Usage: make deploy SUBSCRIPTION=<id> RESOURCE_GROUP=<name>"; \
		exit 1; \
	fi
	python scripts/deploy_azure.py \
		--subscription $(SUBSCRIPTION) \
		--resource-group $(RESOURCE_GROUP) \
		--location $(or $(LOCATION),eastus)

destroy:
	@if [ -z "$(RESOURCE_GROUP)" ]; then \
		echo "Usage: make destroy RESOURCE_GROUP=<name>"; \
		exit 1; \
	fi
	python scripts/destroy_azure.py \
		--resource-group $(RESOURCE_GROUP) \
		--yes

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
