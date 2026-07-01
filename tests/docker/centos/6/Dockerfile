FROM centos:6

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo \
    && sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo \
    && yum install -y \
    centos-release-scl \
    epel-release \
    && yum clean all

RUN yum install -y \
    rh-python36 \
    rh-python36-python-pip \
    && yum clean all

RUN id -u spices >/dev/null 2>&1 || useradd spices

USER spices
WORKDIR /home/spices

CMD ["bash", "-c", "source /opt/rh/rh-python36/enable && python3 --version"]
