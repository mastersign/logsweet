FROM alpine:latest

RUN apk update && apk add py3-zmq py3-click

COPY logsweet /app/logsweet

WORKDIR /app
ENTRYPOINT ["/usr/bin/env", "python3", "-m", "logsweet.cli"]
