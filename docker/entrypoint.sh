#!/usr/bin/env bash
# 2MHDBMRIPS GEN-5.0-PRA container entrypoint.
# Probe hardware; fall back to mock if silicon is absent; then start the twin.
set -euo pipefail

echo "[entrypoint] 2MHDBMRIPS GEN-5.0-PRA digital twin starting..."

# Default to mock unless the host explicitly provides FPGA access.
: "${FPGA_MOCK:=1}"

if [ -e /dev/fpga0 ] || [ "${HIL_ENABLED:-0}" = "1" ]; then
    echo "[entrypoint] Hardware interface detected — attempting live HIL."
    export FPGA_MOCK=0
else
    echo "[entrypoint] No hardware detected — running in mock mode (FPGA_MOCK=1)."
    export FPGA_MOCK=1
fi

echo "[entrypoint] PYTHONPATH=${PYTHONPATH:-unset}  FPGA_MOCK=${FPGA_MOCK}"
exec "$@"
