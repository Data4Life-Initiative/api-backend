POSTGRESQL_VOLUME := postgres_data
PROJECT_NAME := data4life-backend
DJANGO_CONTAINER_NAME := django

GCLOUD_HOSTNAME = eu.gcr.io
GCLOUD_PROJECTID = public-data4life

DEPLOY_VERSION_FILE = ./deploy_version
DEPLOY_VERSION = $(shell test -f $(DEPLOY_VERSION_FILE) && cat $(DEPLOY_VERSION_FILE))

GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD | sed -E 's/[^a-zA-Z0-9]+/-/g')
GIT_COMMIT := $(shell git rev-parse --short HEAD)

DOCKER_IMAGE := ${GCLOUD_HOSTNAME}/${GCLOUD_PROJECTID}/$(PROJECT_NAME)
DOCKER_TAG := $(GIT_BRANCH)-$(shell date +%Y%m%d%H%M%S)-$(GIT_COMMIT)

.DEFAULT_GOAL := help

#help:	@ List available tasks on this project
help:
		@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#build:	@ builds the python and postgresql container images
build:
		@docker-compose -p data4life_backend build

#start:	@ starts the python and postgresql containers
start:
		@docker-compose -p data4life_backend up -d

#restart_django: @ restarts the python container
restart_django:
		@docker restart ${DJANGO_CONTAINER_NAME}

#stop:	@ stops the python and postgresql containers
stop:
		@docker-compose -p data4life_backend down

#cleanup:	@ deletes the named volume created for postgresql container
cleanup:
		@docker volume rm data4life_backend_$(POSTGRESQL_VOLUME)

#migrations: @ generates the migration files to be applied based on db schema changes
migrations:
		@docker-compose exec web python manage.py makemigrations

#migrate:	@ migrates the database schema changes
migrate:
		@docker-compose exec web python manage.py migrate --noinput

#initdb:	@ initializes database with predefined data
initdb:
		@docker-compose exec web python initdb.py

#djangologs:	@ watch logs for django
djangologs:
		@docker container logs -f $(DJANGO_CONTAINER_NAME)

#build-keycloak-deployable-image: @ builds keycloak docker image for deployment
build-keycloak-deployable-image:
		docker build -t $(GCLOUD_HOSTNAME)/$(GCLOUD_PROJECTID)/iam:latest -f resources/docker/iam/production/Dockerfile .

#publish-keycloak-image: @ publishes keycloak image to eu.gcr.io
publish-keycloak-image:
		@gcloud docker -- push $(GCLOUD_HOSTNAME)/$(GCLOUD_PROJECTID)/iam:latest

#set-keycloak-image-staging: @ updates staging keycloak image with the deployed image
set-keycloak-image-staging:
		kubectl set image deployment/data4life-iam-deployment data4life-iam=$(GCLOUD_HOSTNAME)/$(GCLOUD_PROJECTID)/iam:latest -n staging

#build-django-deployable-image: @ builds django docker image for deployment
.PHONY: build-django-deployable-image
build-django-deployable-image:
		docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f resources/docker/production/Dockerfile .
		echo "$(DOCKER_IMAGE):$(DOCKER_TAG)" > $(DEPLOY_VERSION_FILE)

#publish-django-image: @ publishes django image to eu.gcr.io
.PHONY: publish-django-image
publish-django-image:
		@gcloud docker -- push $(DEPLOY_VERSION)

#set-django-image-staging: @ updates staging django image with deployed image
.PHONY: set-django-image-staging
set-django-image-staging:
		kubectl set image deployment/django django=$(DEPLOY_VERSION) -n staging