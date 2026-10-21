#!/bin/bash

# 脚本名称: restart_service.sh
# 功能: 重启 service_audio_ana.py 服务

# 定义程序名称变量
SERVICE_NAME="service_gen_email.py"

# 查找并终止已存在的进程
echo "正在检查已存在的 ${SERVICE_NAME} 进程..."
pid=$(ps aux | grep "${SERVICE_NAME}" | grep -v grep | awk '{print $2}')

if [ -n "$pid" ]; then
    echo "找到进程 PID: $pid，正在终止..."
    # 获取进程占用的端口号
    port=$(netstat -tulpn 2>/dev/null | grep "$pid" | awk '{print $4}' | cut -d':' -f2)
    if [ -n "$port" ]; then
        echo "进程占用端口: $port"
    fi
    kill -9 $pid
    sleep 2
    echo "进程已终止。"
else
    echo "未找到正在运行的 ${SERVICE_NAME} 进程。"
fi

# 启动新进程
echo "正在启动 ${SERVICE_NAME}..."
nohup python ${SERVICE_NAME} > /dev/null 2>&1 &

pid=$(ps aux | grep "${SERVICE_NAME}" | grep -v grep | awk '{print $2}')
echo "服务已成功重启，进程号: $pid"