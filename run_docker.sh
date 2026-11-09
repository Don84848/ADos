#!/usr/bin/env bash
# Helper script to run ADos builder inside Docker on Linux / macOS

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
IMAGE_NAME="ados-builder:latest"

if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "[*] Building ADos Docker builder image..."
    docker build -t "$IMAGE_NAME" "$DIR"
fi

echo "[*] Launching ADos builder container..."
docker run --rm -it -v "$DIR:/build" "$IMAGE_NAME" "$@"
