.PHONY: build run start stop clear dcs

IMAGE_NAME := hcs-exporter
CONTAINER_NAME_OBS := hcs-obs-exporter-container
CONTAINER_NAME_DCS := hcs-dcs-exporter-container

build:
	@docker build -t $(IMAGE_NAME) .

run-obs:
	@docker run -d --name $(CONTAINER_NAME_OBS) \
	-v $(shell pwd)/conf:/app/conf \
	-e AccessKeyID=$(AccessKeyID) \
	-e SecretAccessKey=$(SecretAccessKey) \
	$(IMAGE_NAME)

run-dcs:
	@docker run -d --name $(CONTAINER_NAME_DCS) \
	-v $(shell pwd)/conf:/app/conf \
	-e IAM_ENDPOINT=$(IAM_ENDPOINT) \
	-e OC_ENDPOINT=$(OC_ENDPOINT) \
	-e DOMAIN_NAME=$(DOMAIN_NAME) \
	-e USERNAME=$(USERNAME) \
	-e PASSWORD=$(PASSWORD) \
	$(IMAGE_NAME) python entrypoint.py dcs

stop-obs:
	@docker stop $(CONTAINER_NAME_OBS) && docker rm $(CONTAINER_NAME_OBS)

stop-dcs:
	@docker stop $(CONTAINER_NAME_DCS) && docker rm $(CONTAINER_NAME_DCS)

stop-all:
	@docker stop $(CONTAINER_NAME_OBS) 2>/dev/null || true && docker rm $(CONTAINER_NAME_OBS) 2>/dev/null || true
	@docker stop $(CONTAINER_NAME_DCS) 2>/dev/null || true && docker rm $(CONTAINER_NAME_DCS) 2>/dev/null || true

clear:
	@docker rmi $(IMAGE_NAME)

start-obs:
	@nohup python obs_exporter.py > obs_exporter.log 2>&1 &

start-dcs:
	@nohup python dcs_exporter.py > dcs_exporter.log 2>&1 &

kill:
	@pkill -f obs_exporter.py
	@pkill -f dcs_exporter.py

log-obs:
	@tail -f obs_exporter.log

log-dcs:
	@tail -f dcs_exporter.log

clean:
	@rm -f obs_exporter.log
	@rm -f dcs_exporter.log
