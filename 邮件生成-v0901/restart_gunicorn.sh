#!/bin/bash

# 定义程序名称变量：文件名称:app名称
SERVICE_NAME="service_tag:app"

# 定义端口变量
PORT=5018

# 查找并终止已存在的进程
echo "正在检查已存在的 gunicorn 进程..."
pid=$(ps aux | grep "gunicorn.*${SERVICE_NAME}" | grep -v grep | awk '{print $2}')

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
    echo "未找到正在运行的 gunicorn ${SERVICE_NAME} 进程。"
fi

# 启动新进程
echo "正在启动 ${SERVICE_NAME}..."
nohup gunicorn -w 9 -k gthread --threads 20 --bind 0.0.0.0:${PORT} -t 3600 --worker-connections 800 --max-requests 1000 ${SERVICE_NAME} > /dev/null 2>&1 &
sleep 3

# 获取新启动的进程ID
NEW_PID=$(ps aux | grep "gunicorn.*${SERVICE_NAME}" | grep -v grep | awk '{print $2}' | head -n 1)
if [ -n "$NEW_PID" ]; then
    echo "新进程 PID: $NEW_PID"
    # 获取新进程占用的端口号
    NEW_PORT=$(netstat -tulpn 2>/dev/null | grep "$NEW_PID" | awk '{print $4}' | cut -d':' -f2 | head -n 1)
    if [ -n "$NEW_PORT" ]; then
        echo "新进程占用端口: $NEW_PORT"
    fi
else
    echo "未能获取到新启动的进程信息"
fi

echo "服务已成功重启。"