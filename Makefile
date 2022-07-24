.PHONY: build run stop deploy lint

include .env
export

build:
	docker-compose build --no-cache bot worker

run:
	docker-compose up -d

stop:
	docker-compose down

deploy:
	make build
	make run

lint:
	black --preview .
	flake8 .