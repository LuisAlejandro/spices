FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN id -u spices >/dev/null 2>&1 || useradd --create-home spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 