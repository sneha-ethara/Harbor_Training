#!/bin/bash
set -eu

mkdir -p /logs/verifier
python -m rewardkit /tests \
  --workspace /workspace/repo \
  --output /logs/verifier/reward.json \
  --max-concurrent-programmatic 1
