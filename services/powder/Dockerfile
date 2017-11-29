FROM golang:1.9.2-stretch

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y nodejs npm

RUN go get github.com/jteeuwen/go-bindata/...
RUN go install github.com/jteeuwen/go-bindata/

ADD client/package.json /go/src/github.com/ructfe-2017/services/powder/client/
ADD client/public /go/src/github.com/ructfe-2017/services/powder/client/public
ADD client/src /go/src/github.com/ructfe-2017/services/powder/client/src

RUN /usr/bin/npm install --prefix /go/src/github.com/ructfe-2017/services/powder/client
RUN /usr/bin/npm run --prefix /go/src/github.com/ructfe-2017/services/powder/client build

RUN go-bindata -o /go/src/github.com/ructfe-2017/services/powder/bindata.go -prefix '/go/src/github.com/ructfe-2017/services/powder/client/build/' /go/src/github.com/ructfe-2017/services/powder/client/build/ /go/src/github.com/ructfe-2017/services/powder/client/build/static/js /go/src/github.com/ructfe-2017/services/powder/client/build/static/css

ADD *.go /go/src/github.com/ructfe-2017/services/powder/

RUN go get github.com/ructfe-2017/services/powder
RUN go install github.com/ructfe-2017/services/powder

ENTRYPOINT /go/bin/powder

EXPOSE 8080
