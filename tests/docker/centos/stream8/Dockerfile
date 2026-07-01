FROM quay.io/centos/centos:stream8

RUN dnf install -y \
    python3 \
    python3-pip \
    && dnf clean all

RUN id -u spices >/dev/null 2>&1 || useradd spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 