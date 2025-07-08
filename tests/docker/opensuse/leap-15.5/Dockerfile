FROM opensuse/leap:15.5

RUN zypper install -y \
    python3 \
    python3-pip \
    && zypper clean -a

RUN useradd --uid 1000 -m spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 