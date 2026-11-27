# macOS Setup Guide: ROS 2 Jazzy (RoboStack + Pixi) & CoppeliaSim

This guide lets macOS students (especially Apple Silicon `arm64`) run **ROS 2 Jazzy** natively alongside **CoppeliaSim** without a virtual machine, and includes the macOS-specific fix for the `libsimExtROS2.dylib` / `_PyExc_RuntimeError` plugin crash.

---

## 1. Install Pixi & ROS 2 Jazzy (RoboStack)

1. Install **Pixi**:
   ```bash
   curl -fsSL https://pixi.sh/install.sh | bash
   ```
   Restart your terminal (or run `source ~/.zshrc`) so `pixi` is on your `PATH`.

2. Create a Pixi workspace with the RoboStack Jazzy channel:
   ```bash
   mkdir -p ~/ros_jazzy_pixi && cd ~/ros_jazzy_pixi
   pixi init -c https://prefix.dev/robostack-jazzy -c https://prefix.dev/conda-forge
   ```

3. Add ROS 2 Jazzy Desktop, build tools, and CoppeliaSim Python IPC dependencies (`pyzmq`, `cbor2`):
   ```bash
   pixi add ros-jazzy-desktop colcon-common-extensions ros-jazzy-teleop-twist-keyboard ros-jazzy-plotjuggler-ros pyzmq cbor2
   ```

4. *(Recommended)* Pin local discovery in `~/ros_jazzy_pixi/pixi.toml` so nodes on the same Mac always discover each other cleanly:
   ```bash
   printf '\n[activation.env]\n' >> ~/ros_jazzy_pixi/pixi.toml
   printf 'ROS_AUTOMATIC_DISCOVERY_RANGE = "LOCALHOST"\n' >> ~/ros_jazzy_pixi/pixi.toml
   printf 'ROS_DOMAIN_ID = "42"\n' >> ~/ros_jazzy_pixi/pixi.toml
   ```

5. Verify ROS 2 works:
   ```bash
   cd ~/ros_jazzy_pixi
   pixi run ros2 run demo_nodes_cpp talker
   ```
   In a second terminal:
   ```bash
   cd ~/ros_jazzy_pixi
   pixi run ros2 run demo_nodes_py listener
   ```
   You should see `Hello World` messages published and received.

---

## 2. Install CoppeliaSim

1. Download **CoppeliaSim Edu** for **macOS (Apple Silicon / arm64)** from the official downloads page: https://downloads.coppeliarobotics.com (or https://www.coppeliarobotics.com).
2. Open the downloaded archive and move `coppeliaSim.app` into `/Applications/coppeliaSim.app`.

---

## 3. Build `sim_ros2_interface` with the macOS Python Fix

### Why this is needed on macOS
When starting a ROS 2 simulation in CoppeliaSim on macOS, it fails by default with:
```text
[CoppeliaSim:error] Cannot load library libsimExtROS2.dylib: (dlopen(...): symbol not found in flat namespace '_PyExc_RuntimeError')
plugin 'ROS2': load failed.
```
ROS 2 message packages (`rosidl_generator_py`) depend on Python C-API symbols, but the upstream `sim_ros2_interface` `CMakeLists.txt` only searches for `Interpreter` and does not link `Python3::Python`. Under macOS `dyld`, unlinked Python symbols cannot be resolved at runtime.

### Steps

1. Clone `simROS2` into a ROS 2 workspace:
   ```bash
   mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
   git clone https://github.com/CoppeliaRobotics/simROS2.git sim_ros2_interface
   ```

2. Patch `CMakeLists.txt` to explicitly link `Python3::Python`:
   ```bash
   python3 -c '
   import os
   p = os.path.expanduser("~/ros2_ws/src/sim_ros2_interface/CMakeLists.txt")
   s = open(p).read()
   s = s.replace("find_package(Python3 REQUIRED COMPONENTS Interpreter)",
                 "find_package(Python3 REQUIRED COMPONENTS Interpreter Development)", 1)
   s = s.replace("target_link_libraries(simROS2 PRIVATE Boost::boost)",
                 "target_link_libraries(simROS2 PRIVATE Boost::boost Python3::Python)", 1)
   open(p, "w").write(s)
   '
   ```

3. Add the lab message types (`Pose2D`, `PoseStamped`, `Clock`, `Imu`) to `meta/interfaces.txt`:
   ```bash
   printf '%s\n' \
     geometry_msgs/msg/PoseStamped \
     rosgraph_msgs/msg/Clock \
     sensor_msgs/msg/Imu \
     geometry_msgs/msg/Pose2D \
     >> ~/ros2_ws/src/sim_ros2_interface/meta/interfaces.txt
   ```

4. Build cleanly inside the Pixi environment (this automatically links the plugin and Lua scripts into CoppeliaSim):
   ```bash
   cd ~/ros2_ws
   export COPPELIASIM_ROOT_DIR="/Applications/coppeliaSim.app/Contents/Resources"
   pixi run --manifest-path ~/ros_jazzy_pixi/pixi.toml colcon build --symlink-install --cmake-clean-cache
   ```

---

## 4. Wrap CoppeliaSim so Applications/Finder Launches Inherit ROS 2

macOS GUI apps launched from Applications, Finder, or Spotlight do not inherit your terminal's `AMENT_PREFIX_PATH`. Wrapping the launcher (and removing the old bundle signature) lets you open **CoppeliaSim** directly from Applications:

1. Rename the original binary to `coppeliaSim_bin`:
   ```bash
   mv /Applications/coppeliaSim.app/Contents/MacOS/coppeliaSim \
     /Applications/coppeliaSim.app/Contents/MacOS/coppeliaSim_bin
   ```

2. Create the ROS 2 wrapper script at `/Applications/coppeliaSim.app/Contents/MacOS/coppeliaSim`:
   ```bash
   printf '%s\n' \
     '#!/usr/bin/env bash' \
     'if [ -z "$AMENT_PREFIX_PATH" ]; then' \
     '    MANIFEST="$HOME/ros_jazzy_pixi/pixi.toml"' \
     '    hook="$("$HOME/.pixi/bin/pixi" shell-hook -s bash --manifest-path "$MANIFEST" 2>/dev/null)"' \
     '    eval "$hook"' \
     'fi' \
     'export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST' \
     'export ROS_DOMAIN_ID=42' \
     'export COPPELIASIM_ROOT_DIR="/Applications/coppeliaSim.app/Contents/Resources"' \
     'exec "$(dirname "$0")/coppeliaSim_bin" "$@"' \
     > /Applications/coppeliaSim.app/Contents/MacOS/coppeliaSim
   chmod +x /Applications/coppeliaSim.app/Contents/MacOS/coppeliaSim
   ```

3. Remove the stale code signature and quarantine flags so macOS does not report the modified app as damaged:
   ```bash
   rm -rf /Applications/coppeliaSim.app/Contents/_CodeSignature
   xattr -cr /Applications/coppeliaSim.app
   ```

---

## 5. Verify Everything Together

1. In CoppeliaSim, open a ROS 2 lab scene and press **Play**.
2. Confirm there are no `simROS2` or `plugin 'ROS2': load failed` errors in the CoppeliaSim console.
3. In a second terminal, run `cd ~/ros_jazzy_pixi && pixi run ros2 topic list` and confirm the simulation topics appear.

---

## 6. Daily Workflow (Quick Reference)

Once setup is complete, you never need to rebuild unless you edit `sim_ros2_interface`. Whenever you want to work on a lab, use two terminals:

- **Applications / Terminal 1 (Start CoppeliaSim with ROS 2):**
  Open **CoppeliaSim** directly from Applications/Spotlight (or run `/Applications/coppeliaSim.app/Contents/MacOS/coppeliaSim` in Terminal).
- **Terminal 2 (Run ROS 2 nodes, topics, and tools):**
  ```bash
  cd ~/ros_jazzy_pixi
  pixi shell
  ```
  Inside that shell, run any ROS 2 command (e.g., `ros2 topic list`, `ros2 topic echo /odom`, `ros2 run teleop_twist_keyboard teleop_twist_keyboard`, or `plotjuggler`).
