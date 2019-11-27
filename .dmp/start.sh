#!/bin/sh

SERVICE=$1

nohup python /home/work/code/pytorch_car_classifier/classifier_train.py >> /home/work/logs/pytorch_car_classifier/train.log

# 启动nginx 
nginx

#由于k8s中要求镜像启动脚本必须挂在前台不退出，这里用tail一个文件的方式解决。
tail -f /home/work/var/pytorch_car_classifier/nginx/access.log
