#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "${DIR}/ros_ws"

echo "Checking Docker status..."
if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running. Please start Docker Desktop and ensure it is ready."
    exit 1
fi

echo "Starting ROS 2 Jazzy Desktop VNC container..."
docker run -d \
  --name ros2-lab \
  -p 6080:80 \
  --shm-size=512m \
  --security-opt seccomp=unconfined \
  -v "${DIR}/ros_ws:/home/ubuntu/ros_ws" \
  tiryoh/ros2-desktop-vnc:jazzy 2>/dev/null || docker start ros2-lab

echo ""
echo "=================================================="
echo "ROS 2 Jazzy Container is running!"
echo "Open your browser to: http://localhost:6080"
echo "Shared code folder: ${DIR}/ros_ws"
echo "To stop: docker stop ros2-lab"
echo "=================================================="
