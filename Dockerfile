FROM alpine:3.18

COPY . /relay

WORKDIR /relay

RUN apk update && \
    apk add --no-cache python3 py3-pip tzdata rsync && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "-u", "relay.py"]