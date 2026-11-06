FROM ghcr.io/astral-sh/uv:0.8.17 AS uv
FROM golang:1.23

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=uv /uv /uvx /usr/local/bin/
RUN mkdir -p /workspace/repo /tests/data
WORKDIR /workspace/repo
COPY test.sh build.py no_python.py behaviour.py reward.toml /tests/
COPY data/hidden_inputs.txt data/hidden_expected.txt /tests/data/
RUN chmod +x /tests/test.sh
