#!/bin/sh

#获取项目根目录下.gitlab-ci.yml文件中配置的版本
VERSION=$1
TAGNAME="jelly54.github.io/mirror/pytorch_car_classifier"

#目录初始化，ROOTDIR为项目根目录，SCRIPTDIR为脚本所在目录，也就是项目跟目录下的 .dmp
SCRIPTDIR="$( cd "$( dirname "$0"  )" && pwd  )"
ROOTDIR="$( cd $SCRIPTDIR/.. && pwd )"

#在脚本目录下创建code目录，并把项目根目录下的文件（.开头的文件不会拷贝）拷贝到脚本所在目录
if [ -d "${SCRIPTDIR}/code" ]; then
rm -r $SCRIPTDIR/code/ && mkdir -p  $SCRIPTDIR/code && cp -r  $ROOTDIR/* $SCRIPTDIR/code
else
mkdir -p  $SCRIPTDIR/code && cp -r  $ROOTDIR/* $SCRIPTDIR/code
fi

# 根据环境应用配置


#进入脚本所在目录，先进行docker login,否则无法拉取和推送镜像。
#之后执行docker build，docker build会自动检测当前目录下的Dockerfile,
#根据Dockerfile配置，生成xxxxxxx:$VERSION 的镜像，推送到镜像仓库。
cd $SCRIPTDIR
#docker login -u aiadmin -p 123456 reg.linkdoc-inc.com
docker build --no-cache -t ${TAGNAME}:$VERSION .
#docker push ${TAGNAME}:$VERSION