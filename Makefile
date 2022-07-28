.PHONY: build run stop deploy lint migrate

include .env
export

VENV=.venv
PYTHON=$(VENV)/bin/python3

build:
	docker-compose build --no-cache bot worker

run:
	docker-compose up -d

stop:
	docker-compose down

lint:
	black --preview .
	flake8 .

makemigrations: ## Create alembic migration
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

migrate:  ## Apply latest alembic migrations
	$(PYTHON) -m alembic upgrade head

deploy:
	make build
	make run
	make migrate