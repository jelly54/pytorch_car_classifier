#!/bin/sh

SERVICE=$1

nohup python -m visdom.server > visdom.log &
nohup python /root/code/pytorch_car_classifier/classifier_train.py >> /root/code/pytorch_car_classifier/train.log &


#由于k8s中要求镜像启动脚本必须挂在前台不退出，这里用tail一个文件的方式解决。
tail -f /root/code/pytorch_car_classifier/train.log
