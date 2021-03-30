PROJECT_ID := cca

SHELL := /bin/bash

build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) build

up:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(COMPOSE) -p $(PROJECT_ID) up -d

dev-up:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "up frontend"
	@echo "------------------------------------------------------------------"
	@docker-compose $(COMPOSE) -p $(PROJECT_ID) up -d dev

geonode-up:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production mode"
	@echo "------------------------------------------------------------------"
	@cd geonode/scripts/spcgeonode; docker-compose up --build -d django geoserver postgres nginx

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Killing in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose $(COMPOSE) -p $(PROJECT_ID) kill

rm: kill
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing production instance!!! "
	@echo "------------------------------------------------------------------"
	@docker-compose $(COMPOSE) -p $(PROJECT_ID) rm

rm-volumes:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Removing all volumes!!!! "
	@echo "------------------------------------------------------------------"
	@docker volume rm $(PROJECT_ID)_certificates $(PROJECT_ID)_database $(PROJECT_ID)_geodatadir $(PROJECT_ID)_pgdumps $(PROJECT_ID)_rabbitmq
	@docker volume rm $(PROJECT_ID)_osm-postgis-data $(PROJECT_ID)_import_queue $(PROJECT_ID)_import_done $(PROJECT_ID)_cache