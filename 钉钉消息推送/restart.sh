#!/bin/bash

echo "正在停止旧进程..."

## Kill service_for_dingding.py
#pkill -f "service_for_dingding.py"
#if [ $? -eq 0 ]; then
#    echo "已停止 service_for_dingding.py"
#else
#    echo "未找到运行中的 service_for_dingding.py 进程"
#fi

# Kill task_schedule_dingding.py
pkill -f "task_schedule_dingding.py"
if [ $? -eq 0 ]; then
    echo "已停止 task_schedule_dingding.py"
else
    echo "未找到运行中的 task_schedule_dingding.py 进程"
fi

# 等待进程完全退出
sleep 2

echo "正在启动新进程..."

## 启动 service_for_dingding.py
#nohup python service_for_dingding.py > service_for_dingding.log 2>&1 &
#echo "已启动 service_for_dingding.py (PID: $!)"

# 启动 task_schedule_dingding.py
nohup python task_schedule_dingding.py > task_schedule_dingding.log 2>&1 &
echo "已启动 task_schedule_dingding.py (PID: $!)"

echo "重启完成！"