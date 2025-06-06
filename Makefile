# Makefile pro MedDocAI Anonymizer

# Proměnné
PYTHON = python3
PIP = pip3
DOCKER = docker
DOCKER_COMPOSE = docker-compose

# Výchozí cíl
.DEFAULT_GOAL := help

# Barvy pro výstup
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help setup install dev test clean docker api app all

help: ## Zobrazí nápovědu
	@echo "$(BLUE)MedDocAI Anonymizer - Makefile commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Kompletní setup projektu
	@echo "$(BLUE)🚀 Spouští kompletní setup projektu...$(NC)"
	$(MAKE) install
	$(MAKE) download-models
	@echo "$(GREEN)✅ Setup dokončen!$(NC)"

install: ## Nainstaluje závislosti
	@echo "$(BLUE)📦 Instaluji závislosti...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev-install: ## Nainstaluje dev závislosti
	@echo "$(BLUE)🔧 Instaluji dev závislosti...$(NC)"
	$(PIP) install pytest pytest-cov black flake8 mypy

download-models: ## Stáhne spaCy modely
	@echo "$(BLUE)🤖 Stahuji spaCy modely...$(NC)"
	$(PYTHON) -m spacy download cs_core_news_sm

test: ## Spustí testy
	@echo "$(BLUE)🧪 Spouští testy...$(NC)"
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html

test-quick: ## Spustí rychlé testy
	@echo "$(BLUE)⚡ Spouští rychlé testy...$(NC)"
	$(PYTHON) -m pytest tests/unit/ -v

lint: ## Spustí linting
	@echo "$(BLUE)🔍 Spouští linting...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check .

format: ## Naformátuje kód
	@echo "$(BLUE)✨ Formátuji kód...$(NC)"
	black .

app: ## Spustí Streamlit aplikaci
	@echo "$(BLUE)🌐 Spouští Streamlit aplikaci...$(NC)"
	$(PYTHON) run_app.py

api: ## Spustí REST API server
	@echo "$(BLUE)🔗 Spouští REST API server...$(NC)"
	$(PYTHON) run_api.py

dev: ## Spustí vývojový režim (app + api)
	@echo "$(BLUE)🔧 Spouští vývojový režim...$(NC)"
	@echo "$(YELLOW)Tip: Spusť 'make app' a 'make api' v separátních terminálech$(NC)"
	$(PYTHON) run_app.py

docker-build: ## Sestaví Docker image
	@echo "$(BLUE)🐳 Sestavuji Docker image...$(NC)"
	$(DOCKER) build -t meddocai-anonymizer .

docker-run: ## Spustí Docker kontejner
	@echo "$(BLUE)🚀 Spouští Docker kontejner...$(NC)"
	$(DOCKER) run -p 8501:8501 -v $(PWD)/uploads:/app/uploads -v $(PWD)/exports:/app/exports meddocai-anonymizer

docker-compose-up: ## Spustí pomocí docker-compose
	@echo "$(BLUE)🎼 Spouští docker-compose...$(NC)"
	$(DOCKER_COMPOSE) up --build

docker-compose-down: ## Zastaví docker-compose
	@echo "$(BLUE)🛑 Zastavuji docker-compose...$(NC)"
	$(DOCKER_COMPOSE) down

clean: ## Vyčistí cache a dočasné soubory
	@echo "$(BLUE)🧹 Čistím cache a dočasné soubory...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

clean-data: ## Vyčistí data složky
	@echo "$(BLUE)🗑️  Čistím data složky...$(NC)"
	@echo "$(YELLOW)⚠️  Toto smaže všechny uploads, exports a logs!$(NC)"
	@read -p "Pokračovat? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	rm -rf uploads/*
	rm -rf exports/*
	rm -rf logs/*

logs: ## Zobrazí aktuální logy
	@echo "$(BLUE)📋 Zobrazuji logy...$(NC)"
	tail -f logs/application.log

backup: ## Vytvoří zálohu projektu
	@echo "$(BLUE)💾 Vytvářím zálohu...$(NC)"
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=logs --exclude=uploads --exclude=exports .

# Performance testy
perf-test: ## Spustí performance testy
	@echo "$(BLUE)⚡ Spouští performance testy...$(NC)"
	$(PYTHON) tests/test_performance.py

# Security kontroly
security-check: ## Spustí bezpečnostní kontroly
	@echo "$(BLUE)🔒 Spouští bezpečnostní kontroly...$(NC)"
	safety check
	bandit -r . -x tests/

# Všechno najednou
all: ## Spustí kompletní CI/CD pipeline
	@echo "$(BLUE)🚀 Spouští kompletní pipeline...$(NC)"
	$(MAKE) clean
	$(MAKE) install
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security-check
	@echo "$(GREEN)✅ Pipeline dokončen úspěšně!$(NC)"

# Rychlé restarty
restart-app: ## Rychlý restart aplikace
	@echo "$(BLUE)🔄 Restartuje aplikaci...$(NC)"
	pkill -f "streamlit run" || true
	sleep 2
	$(MAKE) app

restart-api: ## Rychlý restart API
	@echo "$(BLUE)🔄 Restartuje API...$(NC)"
	pkill -f "uvicorn" || true
	sleep 2
	$(MAKE) api
