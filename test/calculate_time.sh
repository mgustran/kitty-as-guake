#!/usr/bin/env bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command>"
    echo "Example: $0 ls -l"
    exit 1
fi

START=$(date +%s.%N)

"$@"
EXIT_CODE=$?

END=$(date +%s.%N)

ELAPSED=$(echo "$END - $START" | bc)

echo "---------------------------------"
echo "Exec time: $ELAPSED seconds"
echo "Exit code: $EXIT_CODE"

exit $EXIT_CODE