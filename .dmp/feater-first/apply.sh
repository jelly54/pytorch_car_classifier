#!/bin/sh

VERSION=$1

# 当前目录
SCRIPTDIR="$( cd "$( dirname "$0"  )" && pwd  )"

# 项目根目录
ROOTDIR="$( cd $SCRIPTDIR/../.. && pwd )"

YML_Path="${SCRIPTDIR}/docker-compose.yml"

# 更改镜像version
sed -i "s/VERSION/${VERSION}/g" ${YML_Path}
