#!/usr/bin/env bash
# Dừng demo: tắt giao diện và worker; container aai-lab vẫn giữ nguyên.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose stop ui
docker exec aai-lab pkill -f demo_worker.py || true
echo "đã dừng demo"
