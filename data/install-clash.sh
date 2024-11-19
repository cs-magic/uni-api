#!/bin/bash

# 1. 下载并安装 Clash
wget https://api.cs-magic.cn/vpn/clash.zip
unzip clash.zip

tar -xzvf clash_2.0.24_linux_amd64.tar.gz
sudo mv clash /usr/local/bin/clash
sudo chmod +x /usr/local/bin/clash

# 2. 创建必要的目录和文件
sudo mkdir -p /etc/clash
sudo chmod -R 777 /etc/clash
mv config /etc/clash

# 3. 创建系统服务配置文件
sudo cp clash.service /etc/systemd/system/

# 5. 设置权限
sudo chown -R root:root /etc/clash
sudo chmod 644 /etc/systemd/system/clash.service
sudo chmod 644 /etc/clash/config.yaml

# 6. 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable clash
sudo systemctl start clash
#sudo systemctl restart clash

# 7. 检查服务状态
systemctl status clash