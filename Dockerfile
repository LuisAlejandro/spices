FROM dockershelf/python:3.9
LABEL maintainer "Luis Alejandro Martínez Faneyth <luis@collagelabs.org>"

RUN apt-get update && \
    apt-get install sudo python3.9-venv

ADD requirements.txt requirements-dev.txt /root/
RUN pip3 install -r /root/requirements.txt -r /root/requirements-dev.txt
RUN rm -rf /root/requirements.txt /root/requirements-dev.txt

RUN useradd -ms /bin/bash condiment
RUN echo "condiment ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/condiment
USER condiment
WORKDIR /home/condiment/app

CMD tail -f /dev/null