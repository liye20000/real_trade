#!/bin/bash

# 启动 FastAPI 服务，并使用 nohup 和 tee 记录日志
nohup uvicorn web_test:app --host 0.0.0.0 --port 8100 2>&1 | tee web_test.log &

# 等待 uvicorn 服务启动
sleep 1

# 获取 uvicorn 进程的 PID
uvicorn_pid=$(pgrep -f "uvicorn web_test:app")

# 将 PID 保存到文件
echo $uvicorn_pid > web_test.pid

echo "FastAPI 服务已启动，日志保存在 web_test.log 中，PID 保存在 web_test.pid 中。"

