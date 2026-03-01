#!/bin/bash
# stop hook: run pytest to verify nothing is broken before the agent finishes

INPUT=$(cat)
LOOP_COUNT=$(echo "$INPUT" | jq -r '.loop_count // 0')

# Only run on first stop (avoid infinite loops)
if [ "$LOOP_COUNT" -gt 0 ]; then
  exit 0
fi

if [ -d "tests" ]; then
  PYTHON=""
  for PY in python python3; do
    if $PY -c "import pytest" 2>/dev/null; then
      PYTHON="$PY"
      break
    fi
  done

  if [ -n "$PYTHON" ]; then
    TEST_OUT=$($PYTHON -m pytest tests/ -x -q 2>&1)
    TEST_EXIT=$?
    if [ $TEST_EXIT -ne 0 ]; then
      cat <<EOF
{
  "followup_message": "Tests are failing. Please fix them before finishing:\n${TEST_OUT}"
}
EOF
      exit 0
    fi
  fi
fi

exit 0
