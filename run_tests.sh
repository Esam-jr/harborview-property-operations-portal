#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "FAIL: Python is not installed or not in PATH."
  exit 1
fi

UNIT_STATUS=0
API_STATUS=0

echo "Running unit tests..."
PYTHONPATH="$ROOT_DIR/backend" "$PYTHON_BIN" -m pytest unit_tests -q || UNIT_STATUS=$?

echo
echo "Running API tests..."
PYTHONPATH="$ROOT_DIR/backend" "$PYTHON_BIN" -m pytest API_tests -q || API_STATUS=$?

echo
echo "========== TEST SUMMARY =========="
if [[ "$UNIT_STATUS" -eq 0 ]]; then
  echo "unit_tests: PASS"
else
  echo "unit_tests: FAIL (exit code $UNIT_STATUS)"
fi

if [[ "$API_STATUS" -eq 0 ]]; then
  echo "API_tests: PASS"
else
  echo "API_tests: FAIL (exit code $API_STATUS)"
fi

if [[ "$UNIT_STATUS" -eq 0 && "$API_STATUS" -eq 0 ]]; then
  echo "Overall: PASS"
  exit 0
fi

echo "Overall: FAIL"
exit 1
