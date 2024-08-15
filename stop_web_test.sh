#!/bin/bash

# 读取保存的 PID 并终止对应的进程
if [ -f web_entry.pid ]; then
    PID=$(cat web_entry.pid)
    kill $PID
    rm web_entry.pid
    echo "FastAPI 服务已停止。"
else
    echo "找不到 web_entry.pid 文件，服务可能未启动。"
fi
