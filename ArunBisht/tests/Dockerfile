FROM python:3.12-slim

COPY --from=golang:1.23 /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOTOOLCHAIN=local
ENV CGO_ENABLED=0

RUN pip install --no-cache-dir 'harbor-rewardkit>=0.2.4' \
    && mkdir -p /workspace/repo /logs/verifier

WORKDIR /workspace/repo
COPY . /tests/
