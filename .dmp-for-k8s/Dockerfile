FROM centos:7.6

MAINTAINER jelly_54@163.com
USER root
WORKDIR /

# 时区设置
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime  && echo 'Asia/Shanghai' >/etc/timezone 

# 设置系统语言为中文
RUN yum -y install net-tools wget lrzsz kde-l10n-Chinese glibc-common
RUN localedef -c -f UTF-8 -i zh_CN zh_CN.UTF-8
ENV LANG zh_CN.UTF-8
ENV LC_ALL zh_CN.UTF-8

# gcc 编译
RUN yum update -y \
    && yum install -y https://centos7.iuscommunity.org/ius-release.rpm \
    && yum install -y python36u python36u-libs python36u-devel python36u-pip \
    && yum install -y which gcc \
    && yum install -y openldap-devel

# 安装上传服务相关
RUN yum install lrzsz -y \
    && yum install zip -y \
    && yum install unzip -y

# pipenv
RUN pip3.6 install pipenv && ln -s /usr/bin/pip3.6 /bin/pip && rm /usr/bin/python && ln -s /usr/bin/python3.6 /usr/bin/python

# 启动脚本路径
ADD start.sh /usr/bin/start.sh

# 代码路径
ADD code /home/work/code/pytorch_car_classifier

RUN yum install -y nginx && pip install -r /home/work/code/pytorch_car_classifier/requirements.txt


# nginx
RUN mkdir -p /home/work/var/pytorch_car_classifier/nginx /home/work/pytorch_car_classifier/static /home/work/logs/pytorch_car_classifier
RUN touch /home/work/var/pytorch_car_classifier/nginx/access.log
ADD nginx.conf /etc/nginx/