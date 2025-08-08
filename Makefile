.PHONY: build run stop clear

IMAGE_NAME := hcs-exporter
CONTAINER_NAME := hcs-exporter-container

build:
	@docker build -t $(IMAGE_NAME) .

run:
	@docker run -d --name $(CONTAINER_NAME) -p 8000:8000 \
		-e AccessKeyID=$(AccessKeyID) \
		-e SecretAccessKey=$(SecretAccessKey) \
		$(IMAGE_NAME)

stop:
	@docker stop $(CONTAINER_NAME) && docker rm $(CONTAINER_NAME)

clear:
	@docker rmi $(IMAGE_NAME)
