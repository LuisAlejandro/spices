FROM centos:7

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo \
    && sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo \
    && yum install -y \
    python3 \
    python3-pip \
    && yum clean all

RUN useradd --uid 1000 spices
USER spices
WORKDIR /home/spices

CMD ["python3", "--version"] 