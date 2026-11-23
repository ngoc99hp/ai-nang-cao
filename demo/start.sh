#!/usr/bin/env bash
# Khởi động demo (chạy trên host, trong thư mục dự án). Không đụng tới stack hpstin.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up -d lab ui
mkdir -p work/queue/in work/queue/out work/logs
if ! docker exec aai-lab pgrep -f demo_worker.py >/dev/null; then
  docker exec -d aai-lab bash -c 'python -W ignore scripts/demo_worker.py > work/logs/demo_worker.log 2>&1'
  echo "worker: đã khởi động"
else
  echo "worker: đang chạy"
fi
echo "Giao diện: http://127.0.0.1:8501 (trên máy khác: ssh -L 8501:127.0.0.1:8501 tuyendv@<server>)"
