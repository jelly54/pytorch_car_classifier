FROM python:3.6

MAINTAINER jelly_54@163.com
USER root
WORKDIR /

# 启动脚本路径
ADD start.sh /usr/bin/start.sh

# 代码路径
ADD code /home/work/code/pytorch_car_classifier

ENV PATH="/usr/local/bin:$PATH"
RUN yum install -y epel-release && yum install -y nginx  && pip install -r /home/work/code/pytorch_car_classifier/requirements.txt

# nginx
RUN mkdir -p /home/work/var/pytorch_car_classifier/nginx /home/work/pytorch_car_classifier/static /home/work/logs/pytorch_car_classifier
RUN touch /home/work/var/pytorch_car_classifier/nginx/access.log
ADD nginx.conf /etc/nginx/