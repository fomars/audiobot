.PHONY: build run stop deploy lint migrate

include .env
export

PYTHON=python3
POSTGRES_DSN="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/postgres"

build:
	docker-compose build bot

run:
	docker-compose up -d --timeout 10

run_new_worker:
	docker run -d --name new_worker --platform linux/x86_64 \
-v /Users/arseny.fomchenko/PycharmProjects/audiobot/mount/output:/app/output \
-v /Users/arseny.fomchenko/PycharmProjects/audiobot/mount/telegram-bot-api:/app/input --env-file .env \
-e REDIS_PORT=6379 -e REDIS_HOST=redis -e API_URL=http://telegram-bot-api:8081/bot --network audiobot_default \
audiobot celery -A app.tasks worker --loglevel=DEBUG

update_api:
	docker-compose pull telegram-bot-api && docker-compose up --detach

stop:
	docker-compose down

lint:
	black --line-length=100 --preview --extend-exclude=versions/ .
	flake8 .

makemigrations: ## Create alembic migration
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

migrate:  ## Apply latest alembic migrations
	$(PYTHON) -m alembic upgrade head

rollback:  ## Rollback last alembic migration
	$(PYTHON) -m alembic downgrade -1

deploy:
	make build
	make run
	docker exec -it bot python3 -m alembic upgrade head  ## apply migrations inside container

drop_db:
	psql "$(POSTGRES_DSN)" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"

create_db:
	psql "$(POSTGRES_DSN)" \
	-c "CREATE DATABASE ${POSTGRES_DB};" \
	-c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};" \
	-c "\c ${POSTGRES_DB};"