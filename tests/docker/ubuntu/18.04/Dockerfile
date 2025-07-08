FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid 1000 --create-home spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 