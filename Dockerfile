FROM alpine:latest

RUN apk add --no-cache \
	python3 \
	py3-click \
	py3-zmq \
	yaml \
	py3-yaml \
	py3-requests

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY logsweet ./logsweet

ENTRYPOINT ["/usr/bin/env", "python3", "-m", "logsweet.cli"]
