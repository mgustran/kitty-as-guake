#!/bin/bash

timestamp=$(date +"%Y%m%d_%H%M%S")

# capture video
ffmpeg -video_size 6400x1440 -framerate 30 -f x11grab -i :0.0 -c:v libx264 -preset ultrafast -crf 18 "captura-$timestamp.mkv"

# generate palette
#ffmpeg -i "captura-$timestamp.mkv" -vf "fps=12,scale=1920:-1:flags=lanczos,palettegen" "palette-$timestamp.png"
ffmpeg -i "captura-$timestamp.mkv" -vf "fps=12,scale=6400:-1:flags=lanczos,palettegen" "palette-$timestamp.png"

# generate gif
#ffmpeg -i "captura-$timestamp.mkv" -i "palette-$timestamp.png" -filter_complex "fps=12,scale=1920:-1:flags=lanczos[x];[x][1:v]paletteuse" "output-$timestamp.gif"
ffmpeg -i "captura-$timestamp.mkv" -i "palette-$timestamp.png" -filter_complex "fps=12,scale=6400:-1:flags=lanczos[x];[x][1:v]paletteuse" "output-$timestamp.gif"