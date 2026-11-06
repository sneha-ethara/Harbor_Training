# Pinned image = the same room every time.
FROM golang:1.23

# Go must never try to download a newer toolchain (the agent has no internet).
ENV GOTOOLCHAIN=local

# Run the agent as a normal user, not root (stops tampering with system files).
RUN useradd --create-home --shell /bin/bash agent

# The original Python project, without its .git folder
# (copied into environment/ first, because Docker can only copy from the build folder).
COPY --chown=agent:agent python-titlecase /workspace/repo

WORKDIR /workspace/repo
