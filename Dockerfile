# syntax=docker/dockerfile:1

# debian:trixie-slim (multi-arch index digest). Same Debian release as the
# runtime image: uv picks wheels for this glibc, and ldconfig is copied over.
FROM debian:trixie-slim@sha256:a29215f6a35e51e22adffa17f89e9d2ef06214e64a2bad10d765c46aea49f11f AS builder

# ghcr.io/astral-sh/uv:0.13.1 (multi-arch index digest)
COPY --from=ghcr.io/astral-sh/uv:0.13.1@sha256:4a1f3666816dafadd20ceb71eac9a7d56d7ef30279f7d64048519ab901ada336 /uv /bin/uv

# The interpreter is uv's standalone CPython for .python-version, installed
# under /python, which the runtime stage copies as is. Bytecode is compiled
# here, as nothing writes .pyc at run time; copy mode, as the cache mount
# can't be hardlinked into the venv.
ENV UV_PYTHON_INSTALL_DIR=/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --locked --no-install-project

COPY *.py ./

# config.json holds the secrets, so it stays out of the image: compose mounts
# it read-only at /etc/spownerbot/config.json, where settings.py looks by
# default.
RUN mkdir /data

# gcr.io/distroless/cc-debian13:latest (multi-arch index digest): glibc and
# libssl, no shell.
FROM gcr.io/distroless/cc-debian13@sha256:159783207c2cd44c2aa5715961d13c8612368ac9bd450f887e3f08fc8ea461e3

# Telethon loads libssl for MTProto's AES through ctypes.util.find_library(),
# which parses `ldconfig -p`; this image has neither ldconfig nor its cache,
# and without them encryption falls back to pure Python, ~30x slower.
COPY --from=builder /usr/sbin/ldconfig /sbin/ldconfig
RUN ["/sbin/ldconfig"]

COPY --from=builder /python /python
COPY --from=builder /app /app
# A fresh named volume inherits this owner and mode; COPY alone would leave
# root:root 0755 and the bot could not write its session.
COPY --from=builder --chown=65532:65532 --chmod=0700 /data /data

ENV PATH=/app/.venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Telethon keeps telethon.session in the working directory.
WORKDIR /data
USER 65532:65532

# SIGINT raises KeyboardInterrupt, which run_until_disconnected() turns into a
# clean disconnect; python as PID 1 would ignore SIGTERM until the SIGKILL.
STOPSIGNAL SIGINT
CMD ["python", "/app/main.py"]
