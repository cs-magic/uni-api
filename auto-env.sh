#!/bin/sh

# 转换.env文件到.env.sample，把值替换为空
if [ -f .env ]; then
    cat .env | sed 's/=.*$/=/' > .env.sample
    # 将修改的.env.sample添加到暂存区
    git add .env.sample
fi
