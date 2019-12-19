FROM nvidia/cuda

MAINTAINER jelly_54@163.com
USER root
WORKDIR /

ENV PYTHONIOENCODING=utf-8
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
ADD sources.list /etc/apt/sources.list

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
RUN curl -so ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh
ENV PATH=/root/miniconda/bin:$PATH
ENV CONDA_AUTO_UPDATE_CONDA=false

# Create a Python 3.6 environment
RUN /root/miniconda/bin/conda create -y --name py36 python=3.6.9 \
 && /root/miniconda/bin/conda clean -ya
ENV CONDA_DEFAULT_ENV=py36
ENV CONDA_PREFIX=/root/miniconda/envs/$CONDA_DEFAULT_ENV
ENV PATH=$CONDA_PREFIX/bin:$PATH
RUN /root/miniconda/bin/conda install conda-build=3.18.9=py36_3 \
 && /root/miniconda/bin/conda clean -ya

# CUDA 10.0-specific steps
RUN conda install -y -c pytorch \
    cudatoolkit=10.0 \
    "pytorch=1.2.0=py3.6_cuda10.0.130_cudnn7.6.2_0" \
    "torchvision=0.4.0=py36_cu100" \
 && conda clean -ya

# Install Requests, a Python library for making HTTP requests
RUN conda install -y requests=2.19.1 \
 && conda clean -ya

# 启动脚本路径
ADD start.sh /usr/bin/start.sh

# 代码路径
ADD code /root/code/pytorch_car_classifier

RUN pip install -r /root/code/pytorch_car_classifier/requirements.txt && touch /root/code/pytorch_car_classifier/train.log
