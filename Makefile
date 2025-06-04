.PHONY: up down bash test migrate

# Start Docker Compose and build if needed
up:
	docker-compose up --build

# Stop and remove containers, networks, volumes
down:
	docker-compose down

# Open bash shell in the web container
bash:
	docker-compose exec web bash

# Run Django tests using pytest
test:
	docker-compose exec web pytest -v

# Run database migrations
migrate:
	docker-compose exec web python manage.py migrate

