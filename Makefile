APP_NAME := $(shell python metadata.py name)
APP_VERSION := $(shell python metadata.py version)
IMAGE_NAME := demsking/$(APP_NAME)

.PHONY: all clean build dist

# Start the development environment using tmuxinator
shell:
	tmuxinator

stop:
	tmux kill-session -t oremi-ohunerin-mqtt

up: certificates
	docker compose up -d --remove-orphans detector

watch: certificates
	docker compose watch listener

config:
	docker compose config

stats:
	docker compose stats

ps:
	docker compose ps

restart:
	docker compose restart

down:
	docker compose down

exec:
	docker compose exec detector bash

logs:
	docker compose logs -f

clean:
	rm -rf dist/ build/

install:
	poetry install

# Show outdated dependencies using poetry
outdated:
	poetry show --outdated

# Update dev env
update:
	poetry update
	devbox update
	pre-commit autoupdate

$(SSL_CERT_FILE):
	mkdir -p $(shell dirname $@)
	openssl req -x509 -nodes -new -sha256 -days 3650 -newkey rsa:2048 \
	  -subj "/C=CM/CN=localhost" \
	  -addext "subjectAltName = DNS:localhost" \
	  -keyout $(SSL_PATH)/localhost-key.pem \
	  -out $(SSL_CERT_FILE)

certificates: $(SSL_CERT_FILE)

help:
	# poetry run oremi-ohunerin-mqtt -h
	docker run -it --rm demsking/oremi-ohunerin-mqtt -h
	docker run -it --rm demsking/oremi-ohunerin-mqtt listen -h

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
	poetry show --outdated

update:
	poetry update
	nix flake update
	pre-commit autoupdate

package:
	rm -rf dist/*
	poetry build --no-cache --format=wheel
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
	  --tag $(IMAGE_NAME):test \
	  --build-arg APP_NAME=$(APP_NAME) \
	  --build-arg APP_VERSION=$(APP_VERSION)

publish: image pypi
	git commit pyproject.toml -m "Release $(APP_VERSION)"
	git tag v$(APP_VERSION)
	git push --tags origin main
