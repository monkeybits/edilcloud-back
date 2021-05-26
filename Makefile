all: init build deploy

init:
	sudo docker swarm init
up:
	docker-compose -f docker-compose.prod.yml up
build:
	docker-compose -f docker-compose.prod.yml up --build
	docker-compose -f docker-compose.prod.yml down
djstripe:
    docker exec -it edilcloud-back_web_1 python manage.py djstripe_sync_models