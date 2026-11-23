#!/usr/bin/env bash
# Khởi động demo (chạy trên host, trong thư mục dự án). Không đụng tới stack hpstin.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work/queue/in work/queue/out
# worker cũ (bản trước chạy trong aai-lab) — tắt nếu còn, để chỉ sandbox nhận job
docker exec aai-lab pkill -f demo_worker.py 2>/dev/null || true
docker compose up -d sandbox ui
echo "Giao diện: http://127.0.0.1:8501 (máy khác: ssh -p 2222 -N -L 8501:127.0.0.1:8501 tuyendv@63.250.52.57)"
