.PHONY: up bash test migrate createsuperuser

# Start Docker Compose
up:
	docker-compose up --build

# Open bash shell inside web container
bash:
	docker-compose exec web bash

# Run Django tests
test:
	docker-compose exec web pytest

# Run DB migrations
migrate:
	docker-compose exec web python manage.py migrate
