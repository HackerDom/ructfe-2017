PORT ?= 8080
DNAME = $(shell basename $(CURDIR))
IMAGE_NAME = `echo $(DNAME) | tr A-Z a-z`

build:
	sudo docker build -t $(IMAGE_NAME) .

run:
	sudo docker run --rm -p $(PORT):$(PORT) $(IMAGE_NAME)
