# Shared science environment for Windows, Linux, and macOS (Intel or Apple Silicon;
# Docker Desktop or OrbStack). The repo is mounted at /work (see compose.yaml), so
# builds write back to the host checkout. Builds natively for amd64 and arm64.

# pyhdf has no arm64 wheel, so build wheels here where the HDF4 headers exist.
# On amd64 pip simply downloads the published wheels.
FROM python:3.12.14-slim AS wheels
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libc6-dev libhdf4-dev \
 && rm -rf /var/lib/apt/lists/*
ENV INCLUDE_DIRS=/usr/include/hdf PIP_DISABLE_PIP_VERSION_CHECK=1
COPY pipeline/requirements-science.lock /tmp/requirements-science.lock
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /tmp/requirements-science.lock

FROM python:3.12.14-slim
# Runtime HDF4 library for a source-built pyhdf (arm64); harmless on amd64.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libhdf4-0 \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY pipeline/requirements-science.lock /tmp/requirements-science.lock
RUN --mount=type=bind,from=wheels,source=/wheels,target=/wheels \
    pip install --no-index --find-links /wheels -r /tmp/requirements-science.lock \
 && python -c "import numpy, h5py, pyproj; from pyhdf.SD import SD"

WORKDIR /work
CMD ["python", "-m", "unittest", "discover", "-s", "pipeline/tests", "-v"]
