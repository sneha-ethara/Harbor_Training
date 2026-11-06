#!/bin/bash
# Verifier entry point. Reward Kit runs every check under /tests and writes
# /logs/verifier/reward.json (one score per check + the weighted "reward").
set -euo pipefail

mkdir -p /logs/verifier
uvx --python '>=3.12,<3.14' --from 'harbor-rewardkit==0.2.*' \
    rewardkit /tests --workspace /workspace/repo --output /logs/verifier/reward.json

cat /logs/verifier/reward.json
