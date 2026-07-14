# 2MHDBMRIPS GEN-5.0-PRA — Digital Twin container
# Multi-stage build: Debian 12 (bookworm) + Python 3.12, no host Python needed.

# ---- Stage 1: builder -------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libhdf5-dev \
        libzmq3-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/2mhd-digital-twin
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: runtime -------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/2mhd-digital-twin \
    FPGA_MOCK=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
        libhdf5-103 \
        libzmq5 \
        qtbase5-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

WORKDIR /opt/2mhd-digital-twin
COPY . /opt/2mhd-digital-twin

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# ZMQ telemetry, Grafana, optional web UI
EXPOSE 5555 8080 3000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "scripts/field_bootstrap.py"]
