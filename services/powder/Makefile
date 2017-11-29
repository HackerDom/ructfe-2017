all:
	npm run --prefix client build
	go-bindata -prefix 'client/build/' client/build client/build/static/js client/build/static/css
	go build
