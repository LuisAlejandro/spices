FROM opensuse/leap:15.5

RUN zypper install -y \
    python3 \
    python3-pip \
    && zypper clean -a

RUN id -u spices >/dev/null 2>&1 || useradd -m spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 