#!/bin/bash
set -e

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set."
  echo "Run: export ANTHROPIC_API_KEY=sk-ant-..."
  exit 1
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT"

echo "Starting Task A (User Modeling) on port 8001..."
cd "$ROOT/task_a"
uvicorn main:app --host 0.0.0.0 --port 8001 &
TASK_A_PID=$!

echo "Starting Task B (Recommendation) on port 8002..."
cd "$ROOT/task_b"
uvicorn main:app --host 0.0.0.0 --port 8002 &
TASK_B_PID=$!

echo ""
echo "Both services running:"
echo "  Task A: http://localhost:8001  (docs: http://localhost:8001/docs)"
echo "  Task B: http://localhost:8002  (docs: http://localhost:8002/docs)"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $TASK_A_PID $TASK_B_PID 2>/dev/null; echo 'Stopped.'" INT TERM
wait
