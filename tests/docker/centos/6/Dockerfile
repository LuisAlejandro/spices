FROM centos:6

RUN yum install -y \
    centos-release-scl \
    epel-release \
    && yum clean all

RUN yum install -y \
    freetype-devel \
    gcc \
    ghostscript \
    lcms2-devel \
    libffi-devel \
    libjpeg-devel \
    libtiff-devel \
    libwebp-devel \
    openjpeg2-devel \
    rh-python36 \
    rh-python36-python-virtualenv \
    sudo \
    tcl-devel \
    tk-devel \
    tkinter \
    xorg-x11-server-Xvfb \
    zlib-devel \
    && yum clean all

RUN useradd --uid 1000 spices

RUN bash -c "source /opt/rh/rh-python36/enable \
    && /opt/rh/rh-python36/root/usr/bin/virtualenv -p python3.6 --system-site-packages /vpy3 \
    && /vpy3/bin/pip install --no-cache-dir --upgrade pip \
    && /vpy3/bin/pip install --no-cache-dir cffi olefile pytest pytest-cov \
    && /vpy3/bin/pip install --no-cache-dir numpy --only-binary=:all: || true \
    && cat /opt/rh/rh-python36/enable /vpy3/bin/activate > /vpy3/bin/activate3.6 \
    && mv /vpy3/bin/activate3.6 /vpy3/bin/activate \
    && chown -R pillow:pillow /vpy3"


USER spices
CMD ["depends/test.sh"]