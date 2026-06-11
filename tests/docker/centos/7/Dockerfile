FROM centos:7

RUN yum install -y \
    python3 \
    python3-pip \
    && yum clean all

RUN useradd --uid 1000 spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 