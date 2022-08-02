.PHONY: build run stop deploy lint migrate

include .env
export

PYTHON=python3
POSTGRES_DSN="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/postgres"

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
	docker exec -it bot python3 -m alembic upgrade head

drop_db:
	psql "$(POSTGRES_DSN)" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"

create_db:
	psql "$(POSTGRES_DSN)" \
	-c "CREATE DATABASE ${POSTGRES_DB};" \
	-c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${DB_USER};" \
	-c "\c ${POSTGRES_DB};"