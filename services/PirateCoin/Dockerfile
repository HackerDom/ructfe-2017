FROM debian:stable-slim

RUN apt-get update && \
	apt-get install -y software-properties-common \
	add-apt-repository -y ppa:ethereum/ethereum \
	apt-get update \
	apt-get install --no-install-recommends -y geth \
	apt-get clean -y && rm -rf /var/cache/debconf/* /var/lib/apt/lists/*
WORKDIR /home/PirateCoin/
