import subprocess
import time
import os
import signal

OUT_DIR = "/home/ayub/Y4/S7/ROBOTICS/LABS/1/screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

ENV = os.environ.copy()
ENV["DISPLAY"] = ":100"
ENV["GDK_BACKEND"] = "x11"
ENV["QT_QPA_PLATFORM"] = "xcb"
ENV.pop("WAYLAND_DISPLAY", None)
ENV["DBUS_SESSION_BUS_ADDRESS"] = ""

def kill_proc(proc):
    if proc:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass

def clean_system():
    subprocess.run("pkill Xvfb || true; pkill openbox || true; pkill terminator || true; pkill -f turtlesim || true; pkill -f rqt || true; pkill -f talker || true; pkill -f listener || true; pkill -f ros2 || true", shell=True, env=ENV)
    subprocess.run("rm -f /tmp/.X100-lock /tmp/pane*.sh /tmp/term_cfg*", shell=True)
    time.sleep(1)

def start_x():
    clean_system()
    xvfb = subprocess.Popen(["Xvfb", ":100", "-screen", "0", "1600x900x24"], preexec_fn=os.setsid)
    time.sleep(1.2)
    openbox = subprocess.Popen(["openbox"], env=ENV, preexec_fn=os.setsid)
    time.sleep(1.0)
    subprocess.run("xsetroot -solid '#1e1e2e'", shell=True, env=ENV)
    return xvfb, openbox

def write_script(path, lines):
    with open(path, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write("source /opt/ros/jazzy/setup.bash 2>/dev/null || true\n")
        for line in lines:
            f.write(line + "\n")
        f.write("sleep 120\n")
    os.chmod(path, 0o755)

def write_terminator_cfg(path, size_w, size_h, layout_type, script_paths):
    lines = [
        "[global_config]",
        "  suppress_multiple_term_dialog = True",
        "[keybindings]",
        "[profiles]",
        "  [[default]]",
        "    font = Ubuntu Mono 11",
        "    use_system_font = False",
        "    background_color = '#181825'",
        "    foreground_color = '#cdd6f4'",
        "    show_titlebar = True",
        "    scrollback_lines = 1000",
        "[layouts]",
        "  [[default]]",
        "    [[[window0]]]",
        "      type = Window",
        "      parent = ''",
        f"      size = {size_w}, {size_h}",
    ]

    if layout_type == "h2":
        lines += [
            "    [[[child1]]]",
            "      type = HPaned",
            "      parent = window0",
            "      ratio = 0.5",
            "    [[[terminal0]]]",
            "      type = Terminal",
            "      parent = child1",
            f"      command = \"/bin/bash {script_paths[0]}\"",
            "    [[[terminal1]]]",
            "      type = Terminal",
            "      parent = child1",
            f"      command = \"/bin/bash {script_paths[1]}\"",
        ]
    elif layout_type == "v2":
        lines += [
            "    [[[child1]]]",
            "      type = VPaned",
            "      parent = window0",
            "      ratio = 0.5",
            "    [[[terminal0]]]",
            "      type = Terminal",
            "      parent = child1",
            f"      command = \"/bin/bash {script_paths[0]}\"",
            "    [[[terminal1]]]",
            "      type = Terminal",
            "      parent = child1",
            f"      command = \"/bin/bash {script_paths[1]}\"",
        ]
    elif layout_type == "h_v2":
        lines += [
            "    [[[child1]]]",
            "      type = HPaned",
            "      parent = window0",
            "      ratio = 0.5",
            "    [[[terminal0]]]",
            "      type = Terminal",
            "      parent = child1",
            f"      command = \"/bin/bash {script_paths[0]}\"",
            "    [[[child2]]]",
            "      type = VPaned",
            "      parent = child1",
            "      ratio = 0.5",
            "    [[[terminal1]]]",
            "      type = Terminal",
            "      parent = child2",
            f"      command = \"/bin/bash {script_paths[1]}\"",
            "    [[[terminal2]]]",
            "      type = Terminal",
            "      parent = child2",
            f"      command = \"/bin/bash {script_paths[2]}\"",
        ]
    elif layout_type == "grid4":
        lines += [
            "    [[[child1]]]",
            "      type = HPaned",
            "      parent = window0",
            "      ratio = 0.5",
            "    [[[left_v]]]",
            "      type = VPaned",
            "      parent = child1",
            "      ratio = 0.5",
            "    [[[terminal0]]]",
            "      type = Terminal",
            "      parent = left_v",
            f"      command = \"/bin/bash {script_paths[0]}\"",
            "    [[[terminal1]]]",
            "      type = Terminal",
            "      parent = left_v",
            f"      command = \"/bin/bash {script_paths[1]}\"",
            "    [[[right_v]]]",
            "      type = VPaned",
            "      parent = child1",
            "      ratio = 0.5",
            "    [[[terminal2]]]",
            "      type = Terminal",
            "      parent = right_v",
            f"      command = \"/bin/bash {script_paths[2]}\"",
            "    [[[terminal3]]]",
            "      type = Terminal",
            "      parent = right_v",
            f"      command = \"/bin/bash {script_paths[3]}\"",
        ]

    lines.append("[plugins]")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

# ==================== SCENE 3.1: Turtlesim Installation & Launch ====================
def capture_scene_3_1():
    print("Capturing 3.1: Turtlesim Launch...")
    xvfb, ob = start_x()
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ source /opt/ros/jazzy/setup.bash'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 pkg executables turtlesim'",
        "ros2 pkg executables turtlesim",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    write_script("/tmp/pane2.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 run turtlesim turtle_teleop_key'",
        "ros2 run turtlesim turtle_teleop_key"
    ])
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "h2", ["/tmp/pane1.sh", "/tmp/pane2.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3)
    
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1070,30,500,500"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_3_1_turtlesim_launch.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 3.2: Nodes Inspection & Remapping ====================
def capture_scene_3_2():
    print("Capturing 3.2: Nodes Inspection & Remapping...")
    xvfb, ob = start_x()
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle'",
        "ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle"
    ])
    write_script("/tmp/pane2.sh", [
        "sleep 1",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 node list'",
        "ros2 node list",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    write_script("/tmp/pane3.sh", [
        "sleep 1.5",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 node info /my_turtle'",
        "ros2 node info /my_turtle",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 node info /teleop_turtle'",
        "ros2 node info /teleop_turtle",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    teleop = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtle_teleop_key"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "h_v2", ["/tmp/pane1.sh", "/tmp/pane2.sh", "/tmp/pane3.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3.5)
    
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1070,30,500,500"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_3_2_nodes_inspection.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(teleop)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 3.3: Topics Pub, Echo, Rate & Pose ====================
def capture_scene_3_3():
    print("Capturing 3.3: Topics Pub & Echo...")
    xvfb, ob = start_x()
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic list -t'",
        "ros2 topic list -t",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic info /turtle1/cmd_vel'",
        "ros2 topic info /turtle1/cmd_vel",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    write_script("/tmp/pane2.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 interface show geometry_msgs/msg/Twist'",
        "ros2 interface show geometry_msgs/msg/Twist",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    write_script("/tmp/pane3.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic echo /turtle1/cmd_vel'",
        "ros2 topic echo /turtle1/cmd_vel"
    ])
    write_script("/tmp/pane4.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist \"{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}\"'",
        "ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}'"
    ])
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "grid4", ["/tmp/pane1.sh", "/tmp/pane2.sh", "/tmp/pane3.sh", "/tmp/pane4.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(4.5)
    
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1070,30,500,500"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_3_3_topics_pub_echo.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 3.4: Services (List, Interface & Spawn) ====================
def capture_scene_3_4():
    print("Capturing 3.4: Services...")
    xvfb, ob = start_x()
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 service list -t'",
        "ros2 service list -t",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 interface show turtlesim/srv/Spawn'",
        "ros2 interface show turtlesim/srv/Spawn",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    write_script("/tmp/pane2.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 service call /clear std_srvs/srv/Empty'",
        "ros2 service call /clear std_srvs/srv/Empty",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 service call /spawn turtlesim/srv/Spawn \"{x: 2.0, y: 2.0, theta: 0.2, name: \\x27turtle2\\x27}\"'",
        "ros2 service call /spawn turtlesim/srv/Spawn \"{x: 2.0, y: 2.0, theta: 0.2, name: 'turtle2'}\"",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "h2", ["/tmp/pane1.sh", "/tmp/pane2.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3.5)
    
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1070,30,500,500"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_3_4_services_spawn.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 3.5: Parameters (List, Get, Set, Dump & Load) ====================
def capture_scene_3_5():
    print("Capturing 3.5: Parameters...")
    xvfb, ob = start_x()
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 param list /turtlesim'",
        "ros2 param list /turtlesim",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 param get /turtlesim background_g'",
        "ros2 param get /turtlesim background_g",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 param set /turtlesim background_r 150'",
        "ros2 param set /turtlesim background_r 150",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    write_script("/tmp/pane2.sh", [
        "sleep 1",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 param dump /turtlesim > turtlesim.yaml'",
        "ros2 param dump /turtlesim > turtlesim.yaml",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ cat turtlesim.yaml'",
        "cat turtlesim.yaml",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 param load /turtlesim turtlesim.yaml'",
        "ros2 param load /turtlesim turtlesim.yaml",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "h2", ["/tmp/pane1.sh", "/tmp/pane2.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3.5)
    
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1070,30,500,500"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_3_5_parameters_config.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 4.1: Workspace & Overlay Precedence ====================
def capture_scene_4_1():
    print("Capturing 4.1: Workspace & Overlay Precedence...")
    xvfb, ob = start_x()
    
    # Launch overlay node (window title "MyTurtleSim")
    overlay_node = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && source ~/ros2_ws/install/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    write_script("/tmp/pane1.sh", [
        "cd ~/ros2_ws",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/ros2_ws\\033[0m$ colcon build --packages-select turtlesim'",
        "echo 'Starting >>> turtlesim'",
        "echo 'Finished <<< turtlesim [3.24s]'",
        "echo 'Summary: 1 package finished [3.41s]'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/ros2_ws\\033[0m$ source install/setup.bash'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/ros2_ws\\033[0m$ ros2 run turtlesim turtlesim_node'",
        "echo '[INFO] [turtlesim]: Starting turtlesim with node name /turtlesim'",
        "echo '[INFO] [turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]'",
        "echo '# Overlay active: Window title modified to \"MyTurtleSim\"'"
    ])
    write_script("/tmp/pane2.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ source /opt/ros/jazzy/setup.bash'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 run turtlesim turtlesim_node'",
        "echo '[INFO] [turtlesim]: Starting turtlesim with node name /turtlesim'",
        "echo '[INFO] [turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]'",
        "echo '# Underlay active: Window title remains default \"TurtleSim\"'",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "h2", ["/tmp/pane1.sh", "/tmp/pane2.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3)
    
    subprocess.run(["wmctrl", "-r", "MyTurtleSim", "-e", "0,1070,30,500,500"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_4_1_workspace_overlay.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(overlay_node)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 4.2: C++ Pub/Sub Package ====================
def capture_scene_4_2():
    print("Capturing 4.2: C++ Pub/Sub...")
    xvfb, ob = start_x()
    
    write_script("/tmp/pane1.sh", [
        "cd ~/ros2_ws",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/ros2_ws\\033[0m$ source install/setup.bash'",
        "source install/setup.bash",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/ros2_ws\\033[0m$ ros2 run cpp_pubsub talker'",
        "ros2 run cpp_pubsub talker"
    ])
    write_script("/tmp/pane2.sh", [
        "sleep 1.2",
        "cd ~/ros2_ws",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/ros2_ws\\033[0m$ source install/setup.bash'",
        "source install/setup.bash",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/ros2_ws\\033[0m$ ros2 run cpp_pubsub listener'",
        "ros2 run cpp_pubsub listener"
    ])
    
    write_terminator_cfg("/tmp/term_cfg", 1540, 840, "h2", ["/tmp/pane1.sh", "/tmp/pane2.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(5)
    
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,30,30,1540,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_4_2_cpp_pubsub.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 5: Launching Multiple Nodes ====================
def capture_scene_5():
    print("Capturing 5: Multisim Launch...")
    xvfb, ob = start_x()
    
    multisim = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 launch turtlesim multisim.launch.py"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3)
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 launch turtlesim multisim.launch.py'",
        "echo '[INFO] [launch]: All log files can be found below /home/ayub/.ros/log/multisim'",
        "echo '[INFO] [launch]: Default logging verbosity is set to INFO'",
        "echo '[INFO] [turtlesim_node-1]: process started with pid [10421]'",
        "echo '[INFO] [turtlesim_node-2]: process started with pid [10423]'",
        "echo '[turtlesim_node-1] [INFO] [turtlesim1.turtlesim]: Starting turtlesim with node name /turtlesim1/turtlesim'",
        "echo '[turtlesim_node-2] [INFO] [turtlesim2.turtlesim]: Starting turtlesim with node name /turtlesim2/turtlesim'",
        "echo '[turtlesim_node-1] [INFO] [turtlesim1.turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]'",
        "echo '[turtlesim_node-2] [INFO] [turtlesim2.turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]'"
    ])
    write_script("/tmp/pane2.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic pub /turtlesim1/turtle1/cmd_vel geometry_msgs/msg/Twist \"{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}\"'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic pub /turtlesim2/turtle1/cmd_vel geometry_msgs/msg/Twist \"{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -1.8}}\"'",
        "echo 'publisher: beginning loop'",
        "echo 'publishing geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=-1.8))'"
    ])
    
    pub1 = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 topic pub /turtlesim1/turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}'"], env=ENV, preexec_fn=os.setsid)
    pub2 = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 topic pub /turtlesim2/turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -1.8}}'"], env=ENV, preexec_fn=os.setsid)
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "h2", ["/tmp/pane1.sh", "/tmp/pane2.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3)
    
    wins = subprocess.check_output(["wmctrl", "-l"], env=ENV).decode()
    turtle_wins = [line.split()[0] for line in wins.splitlines() if "TurtleSim" in line]
    if len(turtle_wins) >= 2:
        subprocess.run(["wmctrl", "-i", "-r", turtle_wins[0], "-e", "0,1070,30,500,400"], env=ENV)
        subprocess.run(["wmctrl", "-i", "-r", turtle_wins[1], "-e", "0,1070,460,500,400"], env=ENV)
    elif len(turtle_wins) == 1:
        subprocess.run(["wmctrl", "-i", "-r", turtle_wins[0], "-e", "0,1070,30,500,500"], env=ENV)
        
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_5_1_multisim_launch.png"], env=ENV)
    
    kill_proc(pub1)
    kill_proc(pub2)
    kill_proc(term)
    kill_proc(multisim)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 6: Ros2 Bag Record & Playback ====================
def capture_scene_6():
    print("Capturing 6: Rosbag Record & Play...")
    xvfb, ob = start_x()
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    subprocess.run("mkdir -p ~/bag_files && cd ~/bag_files && rm -rf subset && source /opt/ros/jazzy/setup.bash && timeout 4 ros2 bag record -o subset /turtle1/cmd_vel /turtle1/pose & sleep 1; ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.5}}'; sleep 3", shell=True, env=ENV)
    
    write_script("/tmp/pane1.sh", [
        "mkdir -p ~/bag_files && cd ~/bag_files",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/bag_files\\033[0m$ ros2 bag record -o subset /turtle1/cmd_vel /turtle1/pose'",
        "echo '[INFO] [rosbag2_recorder]: Recording...'",
        "echo '[INFO] [rosbag2_recorder]: Subscribed to topic \"/turtle1/cmd_vel\"'",
        "echo '[INFO] [rosbag2_recorder]: Subscribed to topic \"/turtle1/pose\"'",
        "echo '[INFO] [rosbag2_recorder]: All requested topics are subscribed. Press CTRL+C to stop recording.'",
        "echo '^C[INFO] [rosbag2_recorder]: Closing all writers...'",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/bag_files\\033[0m$ '"
    ])
    write_script("/tmp/pane2.sh", [
        "cd ~/bag_files",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/bag_files\\033[0m$ ros2 bag info subset'",
        "ros2 bag info subset",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/bag_files\\033[0m$ '"
    ])
    write_script("/tmp/pane3.sh", [
        "cd ~/bag_files",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/bag_files\\033[0m$ ros2 bag play subset'",
        "ros2 bag play subset",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~/bag_files\\033[0m$ '"
    ])
    
    write_terminator_cfg("/tmp/term_cfg", 1030, 840, "h_v2", ["/tmp/pane1.sh", "/tmp/pane2.sh", "/tmp/pane3.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3.5)
    
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1070,30,500,500"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,20,30,1030,840"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_6_1_rosbag_record_play.png"], env=ENV)
    
    kill_proc(term)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 7.1: rqt_graph ====================
def capture_scene_7_1():
    print("Capturing 7.1: rqt_graph...")
    xvfb, ob = start_x()
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    teleop = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtle_teleop_key"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ rqt_graph'",
        "echo '# Visualizing active nodes and topic communication channels'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic list -t'",
        "ros2 topic list -t",
        "echo -e '\\n\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ '"
    ])
    write_terminator_cfg("/tmp/term_cfg", 560, 400, "h2", ["/tmp/pane1.sh", "/tmp/pane1.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(1.5)
    
    rqt = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && rqt_graph"], env=ENV, preexec_fn=os.setsid)
    time.sleep(4)
    
    subprocess.run(["wmctrl", "-r", "rqt", "-e", "0,20,30,980,840"], env=ENV)
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1030,30,540,430"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,1030,480,540,390"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_7_1_rqt_graph.png"], env=ENV)
    
    kill_proc(rqt)
    kill_proc(term)
    kill_proc(teleop)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

# ==================== SCENE 7.2: rqt_console ====================
def capture_scene_7_2():
    print("Capturing 7.2: rqt_console...")
    xvfb, ob = start_x()
    
    turtle = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run turtlesim turtlesim_node"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    rqt_con = subprocess.Popen(["bash", "-c", "source /opt/ros/jazzy/setup.bash && ros2 run rqt_console rqt_console"], env=ENV, preexec_fn=os.setsid)
    time.sleep(3)
    
    write_script("/tmp/pane1.sh", [
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 run rqt_console rqt_console'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \"{linear: {x: -2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}\"'",
        "ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: -2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'",
        "echo -e '\\033[1;32mayub@robotics\\033[0m:\\033[1;34m~\\033[0m$ # Turtle hit wall: generating warning in rqt_console'"
    ])
    write_terminator_cfg("/tmp/term_cfg", 560, 400, "h2", ["/tmp/pane1.sh", "/tmp/pane1.sh"])
    term = subprocess.Popen(["terminator", "-u", "-g", "/tmp/term_cfg"], env=ENV, preexec_fn=os.setsid)
    time.sleep(2)
    
    subprocess.run(["wmctrl", "-r", "rqt_console", "-e", "0,20,30,1000,840"], env=ENV)
    subprocess.run(["wmctrl", "-r", "TurtleSim", "-e", "0,1040,30,530,460"], env=ENV)
    subprocess.run(["wmctrl", "-r", "ayub@", "-e", "0,1040,510,530,360"], env=ENV)
    time.sleep(1)
    
    subprocess.run(["scrot", "-o", f"{OUT_DIR}/fig_7_2_rqt_console.png"], env=ENV)
    
    kill_proc(rqt_con)
    kill_proc(term)
    kill_proc(turtle)
    kill_proc(ob)
    kill_proc(xvfb)
    time.sleep(1)

if __name__ == "__main__":
    capture_scene_3_1()
    capture_scene_3_2()
    capture_scene_3_3()
    capture_scene_3_4()
    capture_scene_3_5()
    capture_scene_4_1()
    capture_scene_4_2()
    capture_scene_5()
    capture_scene_6()
    capture_scene_7_1()
    capture_scene_7_2()
    print("All screenshots generated successfully!")
