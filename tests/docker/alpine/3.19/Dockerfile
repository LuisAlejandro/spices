FROM alpine:3.19

RUN apk add --no-cache \
    python3 \
    py3-pip

RUN adduser -D -u 1000 spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 