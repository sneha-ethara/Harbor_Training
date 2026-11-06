FROM golang:1.23

COPY --from=python-titlecase --exclude=.git . /workspace/repo

WORKDIR /workspace/repo
