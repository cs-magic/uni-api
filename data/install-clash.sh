#!/bin/bash

# 1. 下载并安装 Clash
wget https://api.cs-magic.cn/vpn/clash.zip
unzip clash.zip

# 解析出 clash，会存储到当前目录
tar -xzvf exec/clash_2.0.24_linux_amd64.tar.gz
sudo mv clash /usr/local/bin/clash
sudo chmod +x /usr/local/bin/clash

# 2. 创建必要的目录和文件
sudo mkdir -p /etc/clash
sudo chmod -R 777 /etc/clash
sudo mkdir -p /etc/clash/config
sudo cp -r config/* /etc/clash/config/

# 3. 创建系统服务配置文件
sudo cp clash.service /etc/systemd/system/
sudo chown -R root:root /etc/clash
sudo chmod 644 /etc/systemd/system/clash.service
sudo chmod 644 /etc/clash/config/config.yaml

# 6. 启用
sudo systemctl daemon-reload
sudo systemctl enable clash
sudo systemctl start clash
systemctl status clash

# 6.2 重启
sudo systemctl daemon-reload
sudo systemctl restart clash
systemctl status clash
