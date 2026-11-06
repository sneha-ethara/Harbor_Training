FROM golang:1.23.12-bookworm

# The task must build offline; never let Go try to download a toolchain.
ENV GOTOOLCHAIN=local

WORKDIR /workspace/repo

# The original Python project is the specification the agent must port.
# (Docker can only COPY from the build context, hence environment/repo.)
COPY repo/ /workspace/repo/
