COMPOSE = docker compose

.PHONY: up down logs ps lint fmt test

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

lint:
	ruff check .

fmt:
	black .

test:
	pytest
