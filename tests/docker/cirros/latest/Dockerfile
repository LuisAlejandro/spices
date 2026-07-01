FROM cirros/cirros:latest

# CirrOS is minimal, so we install Python from Alpine
RUN apk add --no-cache \
    python3 \
    py3-pip

RUN id -u spices >/dev/null 2>&1 || adduser -D spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 