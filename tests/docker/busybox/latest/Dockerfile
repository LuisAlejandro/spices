FROM python:3.11-alpine

# BusyBox doesn't have Python by default, so we use python alpine as base
RUN apk add --no-cache busybox

RUN adduser -D -u 1000 spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 