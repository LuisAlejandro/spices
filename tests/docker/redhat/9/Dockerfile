FROM registry.access.redhat.com/ubi9/ubi:latest

RUN dnf install -y \
    python3 \
    python3-pip \
    && dnf clean all

RUN useradd --uid 1000 spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 