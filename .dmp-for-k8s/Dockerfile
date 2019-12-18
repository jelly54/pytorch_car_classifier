FROM anibali/pytorch

MAINTAINER jelly_54@163.com
USER root
WORKDIR /

# 启动脚本路径
ADD start.sh /usr/bin/start.sh

# 代码路径
ADD code /home/user/code/pytorch_car_classifier

RUN pip install -r /home/user/code/pytorch_car_classifier/requirements.txt && touch /home/user/logs/pytorch_car_classifier/train.log
