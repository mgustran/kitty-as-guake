#!/bin/bash

WIDTH=320

while [[ $# -gt 0 ]]; do
  case $1 in
    -w|--width)
      WIDTH="$2"
      shift 2
      ;;
    -*)
      echo "unknown option: $1"
      exit 1
      ;;
    *)
      INPUT="$1"
      shift
      ;;
  esac
done

if [ -z "$INPUT" ]; then
  echo "Usage: $0 [--width <width>] file.mp4"
  exit 1
fi

#INPUT="$1"
BASENAME=$(basename "$INPUT" .mp4)
PALETTE="${BASENAME}_palette.png"
OUTPUT="${BASENAME}.gif"

echo "generating palette..."
ffmpeg -i "$INPUT" -vf "fps=15,scale=${WIDTH}:-1:flags=lanczos,palettegen" "$PALETTE"

echo "generating GIF..."
ffmpeg -i "$INPUT" -i "$PALETTE" -filter_complex "fps=15,scale=${WIDTH}:-1:flags=lanczos[x];[x][1:v]paletteuse" "$OUTPUT"

echo "GIF generated: $OUTPUT"