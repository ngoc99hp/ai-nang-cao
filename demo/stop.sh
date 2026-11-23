#!/usr/bin/env bash
# Dừng demo (giao diện + sandbox chấm bài). Container aai-lab không bị ảnh hưởng.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose stop ui sandbox
echo "đã dừng demo"
