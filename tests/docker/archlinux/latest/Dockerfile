FROM archlinux:latest

RUN pacman -Syu --noconfirm \
    python \
    python-pip \
    && pacman -Scc --noconfirm

RUN useradd --uid 1000 -m spices
USER spices
WORKDIR /home/spices

CMD ["python", "--version"] 