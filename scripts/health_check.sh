#!/usr/bin/env bash
set -euo pipefail

cd /data/.openclaw/workspace
python3 scripts/health_check.py --level daily
