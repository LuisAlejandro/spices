FROM archlinux:latest

RUN pacman -Syu --noconfirm \
    python \
    python-pip \
    && pacman -Scc --noconfirm

RUN id -u spices >/dev/null 2>&1 || useradd -m spices
USER spices
WORKDIR /home/spices

CMD ["python", "--version"] 