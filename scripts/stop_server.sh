#!/bin/bash
set -euo pipefail

echo "[Stop] Stopping Gunicorn..."
sudo systemctl stop gunicorn || true
echo "[Stop] Done."


