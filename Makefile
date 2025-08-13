.PHONY: build run start stop clear

IMAGE_NAME := hcs-exporter
CONTAINER_NAME := hcs-exporter-container

build:
	@docker build -t $(IMAGE_NAME) .

run:
	@docker run -d --name $(CONTAINER_NAME) \
	-v $(shell pwd)/conf:/app/conf \
	-e AccessKeyID=$(AccessKeyID) \
	-e SecretAccessKey=$(SecretAccessKey) \
	$(IMAGE_NAME)

stop:
	@docker stop $(CONTAINER_NAME) && docker rm $(CONTAINER_NAME)

clear:
	@docker rmi $(IMAGE_NAME)

start:
	@nohup python obs_exporter.py > obs_exporter.log 2>&1 &

kill:
	@pkill -f obs_exporter.py

log:
	@tail -f obs_exporter.log

clean:
	@rm -f obs_exporter.log
