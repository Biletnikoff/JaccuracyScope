#!/bin/bash
# afterFileEdit hook: lint the edited file with ruff and check for banned patterns

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

EXT="${FILE_PATH##*.}"
BASENAME=$(basename "$FILE_PATH")
ERRORS=""

# Python file checks
if [ "$EXT" = "py" ]; then
  # Ruff lint
  if command -v ruff &>/dev/null; then
    RUFF_OUT=$(ruff check "$FILE_PATH" 2>&1)
    if [ $? -ne 0 ]; then
      ERRORS="${ERRORS}Ruff errors:\n${RUFF_OUT}\n\n"
    fi
  fi

  # Bare except
  BARE=$(grep -n 'except\s*:' "$FILE_PATH" 2>/dev/null || true)
  if [ -n "$BARE" ]; then
    ERRORS="${ERRORS}Bare except clauses found (use specific exception types):\n${BARE}\n\n"
  fi

  # Direct thread attribute mutation
  THREAD_MUT=$(grep -n 'Threader\.thread\.\w\+\s*=' "$FILE_PATH" 2>/dev/null || true)
  if [ -n "$THREAD_MUT" ]; then
    ERRORS="${ERRORS}Direct thread attribute mutation (use setters or pass via constructor):\n${THREAD_MUT}\n\n"
  fi

  # Hardcoded Pi paths
  HARDCODED=$(grep -n '/home/pi/share/' "$FILE_PATH" 2>/dev/null || true)
  if [ -n "$HARDCODED" ]; then
    ERRORS="${ERRORS}Hardcoded /home/pi/share/ paths (use config.DISPLAY_DIR or ASSETS_DIR):\n${HARDCODED}\n\n"
  fi
fi

# Python and C profanity check
if [ "$EXT" = "py" ] || [ "$EXT" = "c" ] || [ "$EXT" = "h" ]; then
  PROFANITY=$(grep -niE '(shit|fuck|wtf|cock|buttholes)' "$FILE_PATH" 2>/dev/null || true)
  if [ -n "$PROFANITY" ]; then
    ERRORS="${ERRORS}Unprofessional language found:\n${PROFANITY}\n\n"
  fi
fi

if [ -n "$ERRORS" ]; then
  echo -e "$ERRORS" >&2
  exit 2
fi

exit 0
