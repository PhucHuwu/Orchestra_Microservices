COMPOSE = docker compose

.PHONY: up down logs ps lint lint-pylint fmt test bootstrap-topology fault-demo fault-cleanup

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

lint-pylint:
	pylint conductor mixer dashboard/backend/app services scripts

fmt:
	black .

test:
	pytest

bootstrap-topology:
	python scripts/bootstrap_rabbitmq_topology.py

fault-demo:
	python scripts/fault_injection.py run --scenario all

fault-cleanup:
	python scripts/fault_injection.py cleanup --scenario all
