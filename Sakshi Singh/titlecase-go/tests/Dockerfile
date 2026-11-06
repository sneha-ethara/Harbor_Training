FROM golang:1.23.12-bookworm

# uv + a pinned Python 3.12 and RewardKit, so the verifier needs no network at run time.
COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /uvx /usr/local/bin/
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    GOTOOLCHAIN=local \
    PATH=/root/.local/bin:/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin

RUN uv python install 3.12.8 \
    && uv tool install --python 3.12.8 'harbor-rewardkit==0.2.4'

WORKDIR /app

# Tests are baked into the image: Harbor does not upload tests/ into a
# dedicated verifier image, it runs /tests/test.sh from the image.
COPY . /tests/
RUN chmod +x /tests/test.sh
