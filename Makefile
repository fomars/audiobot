.PHONY: build run stop deploy lint migrate

include .env
export

PYTHON=python3
POSTGRES_DSN="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/postgres"

build:
	docker-compose build --no-cache bot worker

run:
	docker-compose up -d

stop:
	docker-compose down

lint:
	black --line-length=100 --preview --extend-exclude=versions/ .
	flake8 .

makemigrations: ## Create alembic migration
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

migrate:  ## Apply latest alembic migrations
	$(PYTHON) -m alembic upgrade head

deploy:
	make build
	make run
	make migrate

drop_db:
	psql "$(POSTGRES_DSN)" -c "DROP DATABASE IF EXISTS ${DB_NAME};"

create_db:
	psql "$(POSTGRES_DSN)" \
	-c "CREATE DATABASE ${DB_NAME};" \
	-c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};" \
	-c "\c ${DB_NAME};"