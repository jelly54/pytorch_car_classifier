FROM nvidia/cuda

MAINTAINER jelly_54@163.com
USER root
WORKDIR /

ENV PYTHONIOENCODING=utf-8
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
ADD ./code/sources.list /etc/apt/sources.list

# Install some basic utilities
RUN apt-get update --fix-missing && \
	apt-get install -y vim net-tools curl wget \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
 && rm -rf /var/lib/rpm/__db*
 
# Install Miniconda
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && wget --quiet https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh -O ~/anaconda.sh && /bin/bash ~/anaconda.sh -b -p /opt/conda && rm ~/anaconda.sh
ENV CONDA_AUTO_UPDATE_CONDA=false
ENV PATH /opt/conda/bin:$PATH

RUN conda install pytorch torchvision -c pytorch -y

# 启动脚本路径
ADD start.sh /usr/bin/start.sh

# 代码路径
ADD code /root/code/pytorch_car_classifier

RUN pip install -r /root/code/pytorch_car_classifier/requirements.txt && touch /root/code/pytorch_car_classifier/train.log
