#!/bin/bash

# 脚本名称: restart_service.sh
# 功能: 重启 task_scheduler.py 服务

# 定义程序名称变量
SERVICE_NAME="task_scheduler.py"
LOG_FILE="task_scheduler.log"
STARTUP_WAIT=3  # 等待进程启动的秒数

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
nohup python ${SERVICE_NAME} > ${LOG_FILE} 2>&1 &
startup_pid=$!

# 等待进程启动
echo "等待进程启动（${STARTUP_WAIT}秒）..."
sleep ${STARTUP_WAIT}

# 验证进程是否仍在运行
pid=$(ps aux | grep "${SERVICE_NAME}" | grep -v grep | awk '{print $2}')

if [ -n "$pid" ]; then
    echo "✓ 服务启动成功，进程号: $pid"

    # 检查日志文件是否有错误
    if [ -f "${LOG_FILE}" ]; then
        error_count=$(grep -iE "error|exception|traceback" ${LOG_FILE} | wc -l)
        if [ "$error_count" -gt 0 ]; then
            echo "⚠ 警告: 日志文件中发现 $error_count 个错误信息"
            tail -n 20 ${LOG_FILE}
        fi
        # 删除日志文件
        rm -f ${LOG_FILE}
    fi
    exit 0
else
    echo "✗ 服务启动失败！进程已退出。"

    # 显示日志文件的最后几行以帮助诊断问题
    if [ -f "${LOG_FILE}" ]; then
        echo ""
        echo "=== 错误日志（最后20行）==="
        tail -n 20 ${LOG_FILE}
        # 删除日志文件
        rm -f ${LOG_FILE}
    fi
    exit 1
fi