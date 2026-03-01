#!/bin/bash
# afterFileEdit hook: recompile C library when C files are edited

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

EXT="${FILE_PATH##*.}"

if [ "$EXT" = "c" ] || [ "$EXT" = "h" ]; then
  BALLS_DIR="$(dirname "$FILE_PATH")"
  if [ -f "$BALLS_DIR/exportme3.c" ]; then
    COMPILE_OUT=$(cd "$BALLS_DIR" && gcc -fPIC -shared -o /dev/null exportme3.c -lm -Wall -Werror 2>&1)
    if [ $? -ne 0 ]; then
      echo "C compilation failed with -Wall -Werror:" >&2
      echo "$COMPILE_OUT" >&2
      exit 2
    fi
  fi
fi

exit 0
