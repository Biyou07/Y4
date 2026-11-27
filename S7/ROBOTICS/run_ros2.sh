#!/usr/bin/env bash
# Quick helper for Lab 2: Introduction to CoppeliaSim & Differential Drive
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXI_DIR="${DIR}/ros_jazzy_pixi"

echo "=========================================================="
echo "  ENSIA Robotics - Lab 2 Native Environment"
echo "=========================================================="
echo "1) CoppeliaSim: /Applications/coppeliaSim.app"
echo "2) ROS 2 Workspace: ~/ros2_ws (sim_ros2_interface compiled)"
echo "3) ROS 2 Jazzy: Managed by Pixi in ${PIXI_DIR}"
echo ""
echo "Helpful commands inside this shell:"
echo "  - Teleoperation:   ros2 run teleop_twist_keyboard teleop_twist_keyboard"
echo "  - Echo odometry:   ros2 topic echo /odom"
echo "  - Echo true pose:  ros2 topic echo /pose"
echo "  - PlotJuggler:     plotjuggler"
echo "  - Record bag:      ros2 bag record -a -o Lab2_\$USER"
echo "=========================================================="
echo "Entering ROS 2 Jazzy shell..."
echo ""

export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export ROS_DOMAIN_ID=42

cd "${PIXI_DIR}"
~/.pixi/bin/pixi shell
