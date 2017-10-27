FROM ubuntu:14.04

LABEL maintainer="werelaxe"


RUN apt-get update && apt-get install curl -y
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get -q -y install mysql-server

RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python3 get-pip.py

RUN mkdir app
COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT service mysql start && mysqladmin -u root password kepler && bash
