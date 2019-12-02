FROM centos:7.6.1810

MAINTAINER jelly_54@163.com
USER root
WORKDIR /

# 启动脚本路径
ADD start.sh /usr/bin/start.sh

# 代码路径
ADD code /home/work/code/pytorch_car_classifier

## 添加个 yum repo，使用阿里云 repo 来加速
RUN mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup && curl -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo

RUN yum install -y epel-release && yum install -y rh-python36 rh-python36-scldevel nginx 

ENV PATH="/opt/rh/rh-python36/root/usr/bin:$PATH"
RUN pip install -r /home/work/code/pytorch_car_classifier/requirements.txt

# nginx
RUN mkdir -p /home/work/var/pytorch_car_classifier/nginx /home/work/pytorch_car_classifier/static /home/work/logs/pytorch_car_classifier
RUN touch /home/work/var/pytorch_car_classifier/nginx/access.log
ADD nginx.conf /etc/nginx/