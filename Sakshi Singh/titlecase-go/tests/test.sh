#!/bin/bash
set -euo pipefail

# RewardKit writes /logs/verifier/reward.json (build/no_python/behaviour -> reward).
export PATH="/root/.local/bin:${PATH}"
rewardkit /tests
