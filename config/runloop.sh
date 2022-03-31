#!/bin/sh
cd /home/orrery/orrery
until $@; do
    echo "$1 exited with exit code $?.  Respawning." >&2
    sleep 1
done
