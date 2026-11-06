# Verifier image: runs in its OWN container, separate from the agent.
# Python 3.12 (for Reward Kit via uvx) + the same pinned Go as the agent image.
FROM python:3.12-slim-bookworm

COPY --from=golang:1.23 /usr/local/go /usr/local/go
ENV PATH=/usr/local/go/bin:$PATH \
    GOTOOLCHAIN=local \
    GOPROXY=off \
    CGO_ENABLED=0 \
    GOFLAGS=-buildvcs=false

RUN pip install --no-cache-dir "uv==0.12.17" \
 && go build std \
 && useradd --create-home runner

# Hidden tests + answer sheets. Only root can read them: the agent's program
# is run as `runner`, so it cannot open the hidden answers and print them.
COPY . /tests/
RUN chmod -R go-rwx /tests

WORKDIR /tests
