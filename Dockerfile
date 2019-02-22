FROM alpine:latest

RUN apk update && apk add \
	py3-click \
	py3-zmq \
	yaml \
	py3-yaml

COPY logsweet /app/logsweet

WORKDIR /app
ENTRYPOINT ["/usr/bin/env", "python3", "-m", "logsweet.cli"]
