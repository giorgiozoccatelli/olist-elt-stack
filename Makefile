.PHONY: up down restart logs ps clean psql

up:
	docker compose up -d

down:
	docke compose down 

restart: down up 

logs:
	docker compose logs -f
	
ps:
	docker compose ps

clean:
	docker compose down -v

psql:
	docker exec -it olist_postgres sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'