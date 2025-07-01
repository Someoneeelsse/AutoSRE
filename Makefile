.PHONY: help build up down logs test clean restart health

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-nginx: ## Show nginx logs
	docker-compose logs -f nginx

test: ## Run all tests
	python3 test_ws.py
	python3 traffic_generator.py --duration 10

test-ws: ## Test WebSocket connection
	python3 test_ws.py

test-traffic: ## Test traffic generation
	python3 traffic_generator.py --duration 30

clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

restart: ## Restart all services
	docker-compose restart

restart-backend: ## Restart backend only
	docker-compose restart backend

restart-frontend: ## Restart frontend only
	docker-compose restart frontend

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health > /dev/null 2>&1 && echo "✅ Backend: OK" || echo "❌ Backend: FAILED"
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "✅ Frontend: OK" || echo "❌ Frontend: FAILED"
	@curl -f http://localhost:8080/health > /dev/null 2>&1 && echo "✅ Nginx: OK" || echo "❌ Nginx: FAILED"

status: ## Show status of all services
	docker-compose ps

rebuild: ## Rebuild and restart all services
	docker-compose down
	docker-compose up --build -d

rebuild-backend: ## Rebuild and restart backend only
	docker-compose stop backend
	docker-compose up --build backend -d

rebuild-frontend: ## Rebuild and restart frontend only
	docker-compose stop frontend
	docker-compose up --build frontend -d

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend /bin/sh

shell-nginx: ## Open shell in nginx container
	docker-compose exec nginx /bin/sh

install-deps: ## Install local development dependencies
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

format: ## Format Python code
	cd backend && black .

lint: ## Lint Python code
	cd backend && flake8 .

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 