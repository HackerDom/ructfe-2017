FROM gcc:latest
RUN apt-get update && \
    apt-get install -y \
        lib3ds-dev \
        libmicrohttpd-dev \
        libmicrohttpd12 \
        uuid-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /home/raster/
CMD ["make", "serve"]
