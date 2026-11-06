#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
# The behaviour worker refuses to start if it can read the hidden tests.
chmod 700 /tests /logs/verifier
exec rewardkit /tests \
    --workspace /workspace/repo \
    --output /logs/verifier/reward.json
