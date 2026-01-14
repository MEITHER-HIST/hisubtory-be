#!/bin/bash
set -euo pipefail

DEPLOY_DIR="/home/ubuntu/django_work/mysite"

echo "[Cleanup] Cleaning old deploy (no EFS)..."

if [ -d "$DEPLOY_DIR" ]; then
  echo "[Cleanup] Removing old directories (keeping 'media' if exists)..."

  # DEPLOY_DIR 바로 아래 디렉터리 중 media 제외하고 삭제
  find "$DEPLOY_DIR" -maxdepth 1 -type d \
    -not -name "media" -not -name "." -not -name ".." \
    -exec rm -rf {} +

  # 임시파일 정리
  find "$DEPLOY_DIR" -maxdepth 1 -type f -name "*.tmp" -delete

  echo "[Cleanup] Done."
else
  echo "[Cleanup] DEPLOY_DIR not found. Skipping."
fi
