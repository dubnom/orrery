#!/bin/sh
cd /home/dubnom/gyre
until $@; do
    echo "$1 exited with exit code $?.  Respawning." >&2
    sleep 1
done
