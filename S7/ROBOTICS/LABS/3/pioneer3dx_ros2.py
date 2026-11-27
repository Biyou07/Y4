#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webots ROS 2 Controller for Pioneer 3-DX Teleoperation & Odometry Lab
ENSIA - Artificial Intelligence and Data Science / Semester 7
Introduction to Mobile Robotics Lab Assignments
"""

import math
import random
from controller import Supervisor

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose2D, TransformStamped
from rosgraph_msgs.msg import Clock
from tf2_ros import TransformBroadcaster


class Pioneer3DXDriver(Node):

    def __init__(self, robot):
        super().__init__('pioneer3dx_driver')

        self.robot = robot
        
        # Supervisor: access the robot's ground-truth state
        self.robot_node = self.robot.getSelf()
        if self.robot_node is None:
            raise RuntimeError("Cannot retrieve the Pioneer robot node")

        # Robot physical parameters (matching CoppeliaSim lab)
        self.wheel_radius = 0.0975         # 19.5 cm / 2
        self.wheel_separation = 0.33       # Robot width
        
        # Frame IDs for ROS 2 / TF
        #self.odom_frame_id = 'odom'
        #self.robot_frame_id = 'base_footprint'
        #self.sensor_ref_frame = 'base_scan'

        # Webots simulation time step
        self.time_step = int(robot.getBasicTimeStep())

        # Wheel motors
        self.left_motor = robot.getDevice("left wheel")
        self.right_motor = robot.getDevice("right wheel")

        # Wheel encoders
        self.left_encoder = robot.getDevice("left wheel sensor")
        self.right_encoder = robot.getDevice("right wheel sensor")

        # Enable velocity control mode
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

        # Enable encoders
        self.left_encoder.enable(self.time_step)
        self.right_encoder.enable(self.time_step)

        # Optional: Hokuyo LiDAR device handle (if present in extensionSlot)
        self.hokuyo = robot.getDevice('fastHokuyo') # adjust name if needed
        if self.hokuyo:
            self.hokuyo.enable(self.time_step)

        # ROS 2 Subscribers and Publishers
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )
        self.pose_pub = self.create_publisher(Pose2D, '/pose', 10)
        self.odom_pub = self.create_publisher(Pose2D, '/odom', 10)
        self.clock_pub = self.create_publisher(Clock, '/clock', 10)

        # TF Broadcaster
        #self.tf_broadcaster = TransformBroadcaster(self)

        # Odometry state variables
        position = self.robot_node.getPosition()
        orientation = self.robot_node.getOrientation()
        yaw = math.atan2(orientation[3], orientation[0])

        self.odom_x = position[0]
        self.odom_y = position[1]
        self.odom_theta = yaw

        # Previous encoder readings
        self.previous_left_encoder = None
        self.previous_right_encoder = None
        
        # Safety watchdog timeout for teleoperation
        self.last_command_time = self.get_clock().now()

        self.get_logger().info('Pioneer 3-DX ROS 2 Driver Initialized successfully.')

    def cmd_vel_callback(self, msg):
        # The message provides the robot linear and angular velocities 
        v = msg.linear.x
        w = msg.angular.z

        L = self.wheel_separation
        r = self.wheel_radius
        
        ##  Calculate the wheel spinning speeds phi_dot_R and phi_dot_L
        ## using the provided linear and angular velocities of the robot.
        ## ---------------------------------------------------------------------
        ## ---------------------------------------------------------------------

        # Differential-drive inverse kinematics
        phi_dot_L = (v - (L / 2.0) * w) / r
        phi_dot_R = (v + (L / 2.0) * w) / r

        # Limit max wheel angular speed
        max_speed = 12.3
        phi_dot_L = max(-max_speed, min(max_speed, phi_dot_L))
        phi_dot_R = max(-max_speed, min(max_speed, phi_dot_R))

        self.left_motor.setVelocity(phi_dot_L)
        self.right_motor.setVelocity(phi_dot_R)

        self.last_command_time = self.get_clock().now()
        
    def publish_clock(self):
        t = self.robot.getTime()
        clock_msg = Clock()
        clock_msg.clock.sec = int(t)
        clock_msg.clock.nanosec = int((t - int(t)) * 1e9)
        self.clock_pub.publish(clock_msg)

    def publish_ground_truth_pose(self):
        position = self.robot_node.getPosition()
        orientation = self.robot_node.getOrientation()

        yaw = math.atan2(orientation[3], orientation[0])
        yaw = math.atan2(math.sin(yaw), math.cos(yaw))

        msg = Pose2D()
        msg.x = position[0]
        msg.y = position[1]
        msg.theta = yaw
        self.pose_pub.publish(msg)



    def update_odometry(self):
        # Read current wheel encoder positions (radians)
        wL_pos = self.left_encoder.getValue()
        wR_pos = self.right_encoder.getValue()

        # Get simulation time step in seconds
        dt = self.time_step / 1000.0

        # Initialize on the first update
        if self.previous_left_encoder is None:
            position = self.robot_node.getPosition()
            orientation = self.robot_node.getOrientation()

            self.odom_x = position[0]
            self.odom_y = position[1]
            self.odom_theta = math.atan2(orientation[3], orientation[0])

            self.previous_left_encoder = wL_pos
            self.previous_right_encoder = wR_pos
            return

        # 1. Compute wheel angular velocity (rad/s) from encoder delta and dt
        
        # Compute incremental angular displacement
        delta_wL = wL_pos - self.previous_left_encoder
        delta_wR = wR_pos - self.previous_right_encoder

        self.previous_left_encoder = wL_pos
        self.previous_right_encoder = wR_pos

        # Angular wheel velocities
        wL_vel = delta_wL / dt
        wR_vel = delta_wR / dt


        # 2. Define noise parameters 
        #noise_mean = 0.05
        #noise_stddev = 0.25

        # Add Gaussian noise to wheel velocities
        #wL_vel += random.gauss(noise_mean, noise_stddev)
        #wR_vel += random.gauss(noise_mean, noise_stddev)

        # 3. Convert noisy angular velocities to linear wheel speeds
        vL = wL_vel * self.wheel_radius
        vR = wR_vel * self.wheel_radius

        # 4. Robot velocities in robot frame
        linear_velocity = (vL + vR) / 2.0
        angular_velocity = (vR - vL) / self.wheel_separation

        # 5. Kinematic integration using mid-point or Euler method 
        theta = self.odom_theta
        x_dot = linear_velocity * math.cos(theta)
        y_dot = linear_velocity * math.sin(theta)
        theta_dot = angular_velocity

        self.odom_x += x_dot * dt
        self.odom_y += y_dot * dt
        self.odom_theta += theta_dot * dt

        # Normalize theta to [-pi, pi]
        self.odom_theta = math.atan2(
            math.sin(self.odom_theta),
            math.cos(self.odom_theta)
        )

        # Publish odometry topic & TF transforms
        msg = Pose2D()
        msg.x = self.odom_x
        msg.y = self.odom_y
        msg.theta = self.odom_theta
        self.odom_pub.publish(msg)

        # Publish TF Transforms (odom -> base_footprint)
        #self.publish_transforms()

        
    def stop_robot(self):
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)
"""
    def publish_transforms(self):
        now = self.get_clock().now().to_msg()

        # 1. odom -> base_footprint transform
        t_odom = TransformStamped()
        t_odom.header.stamp = now
        t_odom.header.frame_id = self.odom_frame_id
        t_odom.child_frame_id = self.robot_frame_id
        t_odom.transform.translation.x = self.odom_x
        t_odom.transform.translation.y = self.odom_y
        t_odom.transform.translation.z = 0.0

        # Convert yaw (theta) to quaternion
        qz = math.sin(self.odom_theta / 2.0)
        qw = math.cos(self.odom_theta / 2.0)
        t_odom.transform.rotation.z = qz
        t_odom.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(t_odom)

        # 2. base_footprint -> base_scan (LiDAR mounting offset relative to robot center)
        t_scan = TransformStamped()
        t_scan.header.stamp = now
        t_scan.header.frame_id = self.robot_frame_id
        t_scan.child_frame_id = self.sensor_ref_frame
        t_scan.transform.translation.x = 0.13  # adjust offset based on your CAD model
        t_scan.transform.translation.y = 0.0
        t_scan.transform.translation.z = 0.23  # height above ground
        t_scan.transform.rotation.w = 1.0     # zero rotation relative to robot base

        self.tf_broadcaster.sendTransform(t_scan)
"""




def main():
    rclpy.init()
    robot = Supervisor()
    node = Pioneer3DXDriver(robot)
    time_step = node.time_step

    try:
        while robot.step(time_step) != -1:
            rclpy.spin_once(node, timeout_sec=0.0)
            
            # Publish simulation clock
            node.publish_clock()

            # Publish ground truth and wheel odometry
            node.publish_ground_truth_pose()
            node.update_odometry()

            # Safety timeout: stop if no /cmd_vel received for 0.5 seconds
            elapsed = (node.get_clock().now() - node.last_command_time).nanoseconds / 1e9
            #if elapsed > 0.5:
            #    node.stop_robot()

    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
