#!/usr/bin/env bash
set -euo pipefail

# Start OpenAI-compatible vLLM server for:
#   marcelbinz/Llama-3.1-Centaur-70B
#
# Requirements:
# - Lambda GPU instance with >=2x 80GB GPUs (e.g. 2x H100 SXM)
# - Access to gated Llama 3.1 weights on Hugging Face
# - HF token exported as HF_TOKEN (or already logged in via huggingface-cli)

MODEL_ID="${MODEL_ID:-marcelbinz/Llama-3.1-Centaur-70B}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
DTYPE="${DTYPE:-bfloat16}"
TP_SIZE="${TP_SIZE:-2}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.92}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-8192}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-$MODEL_ID}"

echo "Starting vLLM server for $MODEL_ID on ${HOST}:${PORT} (tp=${TP_SIZE})"

if ! command -v python >/dev/null 2>&1; then
  echo "python is required on the instance" >&2
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install "vllm>=0.5.0" "huggingface_hub>=0.24.0"

if [[ -n "${HF_TOKEN:-}" ]]; then
  python - <<'PY'
import os
from huggingface_hub import login
token = os.environ.get("HF_TOKEN")
if token:
    login(token=token, add_to_git_credential=False)
PY
fi

exec python -m vllm.entrypoints.openai.api_server \
  --model "${MODEL_ID}" \
  --served-model-name "${SERVED_MODEL_NAME}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --dtype "${DTYPE}" \
  --tensor-parallel-size "${TP_SIZE}" \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  --max-model-len "${MAX_MODEL_LEN}"
