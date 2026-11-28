#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Pose Controller Node for Pioneer 3-DX (Lab 3 - Part 2)
ENSIA - Introduction to Mobile Robotics
Implements bidirectional state feedback pose control with constant-speed
scaling that preserves the v/w path geometry ratio.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D, Twist


class EnhancedPoseController(Node):

    def __init__(self):
        super().__init__('enhanced_pose_controller')

        # 1. Declare parameters with default values
        self.declare_parameter('k_rho', 0.5)
        self.declare_parameter('k_alpha', 1.2)
        self.declare_parameter('k_beta', -0.3)
        self.declare_parameter('v_const', 0.5)             # Constant linear speed [m/s]
        self.declare_parameter('tolerance_dist', 0.1)      # Distance tolerance to goal [m]
        self.declare_parameter('tolerance_theta', 0.05)    # Heading tolerance to goal [rad]
        self.declare_parameter('goal_x', 6.0)              # Target x coordinate
        self.declare_parameter('goal_y', 3.0)              # Target y coordinate
        self.declare_parameter('goal_theta', math.pi / 2)  # Target orientation [rad]
        self.declare_parameter('w_max', 1.2)               # Maximum angular velocity [rad/s]

        # 2. Retrieve parameters
        self.k_rho = self.get_parameter('k_rho').get_parameter_value().double_value
        self.k_alpha = self.get_parameter('k_alpha').get_parameter_value().double_value
        self.k_beta = self.get_parameter('k_beta').get_parameter_value().double_value
        self.v_const = self.get_parameter('v_const').get_parameter_value().double_value
        self.tolerance_dist = self.get_parameter('tolerance_dist').get_parameter_value().double_value
        self.tolerance_theta = self.get_parameter('tolerance_theta').get_parameter_value().double_value
        self.goal_x = self.get_parameter('goal_x').get_parameter_value().double_value
        self.goal_y = self.get_parameter('goal_y').get_parameter_value().double_value
        self.goal_theta = self.get_parameter('goal_theta').get_parameter_value().double_value
        self.w_max = self.get_parameter('w_max').get_parameter_value().double_value

        # Robot current state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        # ROS 2 Subscriber to /pose
        self.pose_sub = self.create_subscription(
            Pose2D,
            '/pose',
            self.pose_callback,
            10
        )

        # ROS 2 Publisher to /cmd_vel
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.get_logger().info(
            f"Enhanced Pose Controller started. Goal: ({self.goal_x:.2f}, {self.goal_y:.2f}, {self.goal_theta:.2f} rad), "
            f"v_const={self.v_const:.2f} m/s, "
            f"Gains: [k_rho={self.k_rho:.2f}, k_alpha={self.k_alpha:.2f}, k_beta={self.k_beta:.2f}]"
        )

    def normalize_angle(self, angle: float) -> float:
        """Wrap angle to [-pi, pi] radians."""
        return math.atan2(math.sin(angle), math.cos(angle))

    def pose_callback(self, msg: Pose2D):
        # Update current robot pose
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta

        # Compute Cartesian errors
        dx = self.goal_x - self.x
        dy = self.goal_y - self.y
        dtheta = self.normalize_angle(self.goal_theta - self.theta)

        # Compute distance to goal
        rho = math.hypot(dx, dy)

        cmd_vel_msg = Twist()

        # Phase 1: Drive towards target position (forward or backward) at constant speed
        if rho > self.tolerance_dist:
            phi = math.atan2(dy, dx)
            alpha = self.normalize_angle(phi - self.theta)

            # Bidirectional logic: reverse if goal is behind the robot (|alpha| > pi/2)
            if abs(alpha) > math.pi / 2.0:
                direction = -1.0
                alpha = self.normalize_angle(alpha - math.pi)
            else:
                direction = 1.0

            beta = self.normalize_angle(self.goal_theta - self.theta - alpha)

            # Raw state feedback control law
            v_raw = direction * self.k_rho * rho
            w_raw = self.k_alpha * alpha + self.k_beta * beta

            # Scale (v, w) to maintain constant speed while preserving v/w ratio
            if abs(v_raw) > 1e-6:
                scale = self.v_const / abs(v_raw)
                v = v_raw * scale
                w = w_raw * scale
            else:
                v = direction * self.v_const
                w = w_raw

            # Respect angular velocity limit while preserving v/w ratio
            if abs(w) > self.w_max:
                limit_scale = self.w_max / abs(w)
                v *= limit_scale
                w *= limit_scale

            cmd_vel_msg.linear.x = float(v)
            cmd_vel_msg.angular.z = float(w)

        # Phase 2: In position, correct remaining orientation error
        elif abs(dtheta) > self.tolerance_theta:
            cmd_vel_msg.linear.x = 0.0
            w = max(-self.w_max, min(1.0 * dtheta, self.w_max))
            cmd_vel_msg.angular.z = float(w)

        # Phase 3: Goal pose reached
        else:
            cmd_vel_msg.linear.x = 0.0
            cmd_vel_msg.angular.z = 0.0
            self.get_logger().info("Goal Reached!", throttle_duration_sec=3.0)

        # Publish velocity command
        self.cmd_vel_pub.publish(cmd_vel_msg)


def main(args=None):
    rclpy.init(args=args)
    node = EnhancedPoseController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
