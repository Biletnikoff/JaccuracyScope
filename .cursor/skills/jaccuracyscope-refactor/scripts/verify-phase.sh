#!/usr/bin/env bash
set -euo pipefail

# Deterministic verification for any refactoring phase.
# Usage: bash scripts/verify-phase.sh [--phase-2a]
#   --phase-2a  Also checks for hardcoded /home/pi/share/ paths

FAIL=0

echo "=== Ruff lint check ==="
if command -v ruff &>/dev/null; then
    ruff check Display/ && echo "PASS" || { echo "FAIL"; FAIL=1; }
else
    echo "SKIP (ruff not installed)"
fi

echo ""
echo "=== C compilation check ==="
if command -v gcc &>/dev/null; then
    cd Display/Balls
    gcc -fPIC -shared -o /dev/null exportme3.c -lm -Wall 2>&1 && echo "PASS" || { echo "FAIL"; FAIL=1; }
    cd ../..
else
    echo "SKIP (gcc not installed -- expected on non-Pi dev machines)"
fi

echo ""
echo "=== Bare except check ==="
BARE=$(grep -rn 'except\s*:' Display/*.py 2>/dev/null || true)
if [ -z "$BARE" ]; then
    echo "PASS"
else
    echo "FAIL -- bare excepts found:"
    echo "$BARE"
    FAIL=1
fi

echo ""
echo "=== Profanity check ==="
PROFANITY=$(grep -rniE '(shit|fuck|wtf|cock|buttholes)' Display/*.py Display/Balls/*.c 2>/dev/null || true)
if [ -z "$PROFANITY" ]; then
    echo "PASS"
else
    echo "FAIL -- unprofessional comments found:"
    echo "$PROFANITY"
    FAIL=1
fi

if [[ "${1:-}" == "--phase-2a" ]]; then
    echo ""
    echo "=== Hardcoded path check ==="
    HARDCODED=$(grep -rn '/home/pi/share/' Display/*.py jaccuracyinstall.sh 2>/dev/null || true)
    if [ -z "$HARDCODED" ]; then
        echo "PASS"
    else
        echo "FAIL -- hardcoded paths found:"
        echo "$HARDCODED"
        FAIL=1
    fi
fi

echo ""
if [ $FAIL -eq 0 ]; then
    echo "=== ALL CHECKS PASSED ==="
else
    echo "=== SOME CHECKS FAILED ==="
    exit 1
fi
