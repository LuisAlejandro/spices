FROM quay.io/fedora/fedora-coreos:stable

RUN rpm-ostree install python3 python3-pip && \
    rpm-ostree cleanup -m && \
    ostree admin unlock --hotfix && \
    /usr/bin/unshare -m /bin/sh -c '/usr/bin/mount -o remount,rw /sysroot && /usr/bin/cp -r /etc/passwd /var/roothome/'

RUN useradd --uid 1000 spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 