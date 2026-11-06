#!/bin/bash

# uvx downloads Reward Kit, so the verifier must have network access.
uvx --python '>=3.12,<3.14' --from 'harbor-rewardkit==0.2.*' \
  rewardkit /tests \
  --workspace /workspace/repo \
  --output /logs/verifier/reward.json
