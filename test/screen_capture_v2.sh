#!/bin/bash

timestamp=$(date +"%Y%m%d_%H%M%S")

GAP=40

LEFT_W=1920
CENTER_W=2560
RIGHT_W=1920
HEIGHT=1440

TOTAL_W=$((LEFT_W + CENTER_W + RIGHT_W + GAP*2))

# capture video
ffmpeg -video_size 6400x1440 -framerate 30 -f x11grab -i :0.0 \
-c:v libx264 -preset ultrafast -crf 18 \
"captura-$timestamp.mkv"

# generate palette
ffmpeg -i "captura-$timestamp.mkv" -filter_complex "
fps=12,
split=3[left][center][right];
[left]crop=${LEFT_W}:${HEIGHT}:0:0[leftc];
[center]crop=${CENTER_W}:${HEIGHT}:${LEFT_W}:0[centerc];
[right]crop=${RIGHT_W}:${HEIGHT}:$((LEFT_W + CENTER_W)):0[rightc];
[leftc]pad=iw+${GAP}:ih:0:0[leftp];
[centerc]pad=iw+${GAP}:ih:0:0[centerp];
[leftp][centerp][rightc]hstack=inputs=3, palettegen
" "palette-$timestamp.png"

# generate final gif
ffmpeg -i "captura-$timestamp.mkv" -i "palette-$timestamp.png" -filter_complex "
fps=12,
split=3[left][center][right];
[left]crop=${LEFT_W}:${HEIGHT}:0:0[leftc];
[center]crop=${CENTER_W}:${HEIGHT}:${LEFT_W}:0[centerc];
[right]crop=${RIGHT_W}:${HEIGHT}:$((LEFT_W + CENTER_W)):0[rightc];
[leftc]pad=iw+${GAP}:ih:0:0[leftp];
[centerc]pad=iw+${GAP}:ih:0:0[centerp];
[leftp][centerp][rightc]hstack=inputs=3[stacked];
[stacked][1:v]paletteuse
" "output-$timestamp.gif"
