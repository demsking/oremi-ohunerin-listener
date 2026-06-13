APP_NAME := $(shell python metadata.py name)
APP_VERSION := $(shell python metadata.py version)
IMAGE_NAME := demsking/$(APP_NAME)

COMPOSE_SERVICES := detector mosquitto

.PHONY: all clean build dist

# Start the development environment using tmuxinator
shell:
	tmuxinator

stop:
	tmux kill-session -t oremi-ohunerin-listener

up: pull
	docker compose -f .devcontainer/workspace.yaml up -d $(COMPOSE_SERVICES) --remove-orphans

logs:
	docker compose -f .devcontainer/workspace.yaml logs -f

pull:
	docker compose -f .devcontainer/workspace.yaml pull $(COMPOSE_SERVICES)

restart:
	docker compose -f .devcontainer/workspace.yaml restart $(COMPOSE_SERVICES)

down:
	docker compose -f .devcontainer/workspace.yaml down $(COMPOSE_SERVICES)

stats:
	docker compose -f .devcontainer/workspace.yaml stats

exec:
	docker compose -f .devcontainer/workspace.yaml exec detector bash

clean:
	rm -rf dist/ build/

install:
	uv sync

# Show outdated dependencies using uv
outdated:
	uv pip list --outdated

# Update dev env
update:
	uv lock --upgrade
	devbox update
	pre-commit autoupdate

help: image-test
	# uv run oremi-ohunerin-listener -h
	docker run -it --rm demsking/oremi-ohunerin-listener:test -h
	docker run -it --rm demsking/oremi-ohunerin-listener:test listen -h

lint:
	pre-commit run --all-files

fix:
	ruff check . --fix

test:
	pytest

coverage:
	pytest --cov=ohunerin

coverage-html:
	pytest --cov=ohunerin --cov-report=html

outdated:
	uv pip list --outdated

update:
	uv lock --upgrade
	devbox update
	pre-commit autoupdate

package:
	rm -rf dist/*
	uv build --wheel
	twine check dist/*

pypi: package
	twine upload dist/*

#
## Packaging
build/context:
	docker buildx create --name $(APP_NAME) --bootstrap
	mkdir -p build/
	touch $@

image: build/context
	docker buildx use $(APP_NAME)
	docker buildx build . \
	  --platform linux/amd64,linux/arm64 \
	  --push \
	  --progress plain \
	  --tag $(IMAGE_NAME):$(APP_VERSION) \
	  --tag $(IMAGE_NAME):latest \
	  --label "org.opencontainers.image.title=$(APP_NAME)" \
	  --label "org.opencontainers.image.description=$(shell python metadata.py description)" \
	  --label "org.opencontainers.image.version=$(APP_VERSION)" \
	  --label "org.opencontainers.image.revision=$(shell git rev-parse HEAD)" \
	  --label "org.opencontainers.image.authors=$(shell python metadata.py authors)" \
	  --label "org.opencontainers.image.created=$(shell date --rfc-3339=seconds)" \
	  --label "org.opencontainers.image.source=$(shell python metadata.py repository)" \
	  --label "org.opencontainers.image.url=$(shell python metadata.py repository)" \
	  --label "org.opencontainers.image.documentation=$(shell python metadata.py documentation)" \
	  --label "org.opencontainers.image.vendor=Oremi" \
	  --label "org.opencontainers.image.licenses=$(shell python metadata.py license)"

image-test:
	docker build --debug . \
	  --progress plain \
	  --tag $(IMAGE_NAME):test

publish: image pypi
	git push --tags origin main
