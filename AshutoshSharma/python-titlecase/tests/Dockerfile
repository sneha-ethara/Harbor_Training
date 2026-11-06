FROM golang:1.23

COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /usr/local/bin/uv

# The behaviour check drops privileges. Python must live outside /root or the
# worker user cannot execute it.
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python

RUN uv python install 3.12 \
    && uv venv /opt/venv --python 3.12 \
    && uv pip install --python /opt/venv/bin/python 'harbor-rewardkit==0.2.4' \
    && chmod -R a+rX /opt/venv /opt/uv-python

ENV PATH="/opt/venv/bin:/usr/local/go/bin:${PATH}"

RUN mkdir -p /workspace /logs/verifier

COPY . /tests/
RUN chmod +x /tests/test.sh
