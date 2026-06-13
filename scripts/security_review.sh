#!/usr/bin/env bash
set -euo pipefail

cd /data/.openclaw/workspace
python3 scripts/security_review.py
