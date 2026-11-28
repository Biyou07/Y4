#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pose Controller Node for Pioneer 3-DX (Lab 3 - Task 6)
ENSIA - Introduction to Mobile Robotics
Implements closed-loop state feedback pose control:
  v = k_rho * rho
  w = k_alpha * alpha + k_beta * beta
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D, Twist


class PoseController(Node):

    def __init__(self):
        super().__init__('pose_controller')

        # 1. Declare parameters with default values
        self.declare_parameter('k_rho', 0.5)
        self.declare_parameter('k_alpha', 1.2)
        self.declare_parameter('k_beta', -0.3)
        self.declare_parameter('tolerance_dist', 0.1)      # Distance tolerance to goal [m]
        self.declare_parameter('tolerance_theta', 0.05)    # Heading tolerance to goal [rad]
        self.declare_parameter('goal_x', 6.0)              # Target x coordinate
        self.declare_parameter('goal_y', 3.0)              # Target y coordinate
        self.declare_parameter('goal_theta', math.pi / 2)  # Target orientation [rad]
        self.declare_parameter('v_max', 0.6)              # Maximum linear velocity [m/s]
        self.declare_parameter('w_max', 1.2)              # Maximum angular velocity [rad/s]

        # 2. Retrieve parameters
        self.k_rho = self.get_parameter('k_rho').get_parameter_value().double_value
        self.k_alpha = self.get_parameter('k_alpha').get_parameter_value().double_value
        self.k_beta = self.get_parameter('k_beta').get_parameter_value().double_value
        self.tolerance_dist = self.get_parameter('tolerance_dist').get_parameter_value().double_value
        self.tolerance_theta = self.get_parameter('tolerance_theta').get_parameter_value().double_value
        self.goal_x = self.get_parameter('goal_x').get_parameter_value().double_value
        self.goal_y = self.get_parameter('goal_y').get_parameter_value().double_value
        self.goal_theta = self.get_parameter('goal_theta').get_parameter_value().double_value
        self.v_max = self.get_parameter('v_max').get_parameter_value().double_value
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
            f"Pose Controller started. Goal: ({self.goal_x:.2f}, {self.goal_y:.2f}, {self.goal_theta:.2f} rad), "
            f"Gains: [k_rho={self.k_rho:.2f}, k_alpha={self.k_alpha:.2f}, k_beta={self.k_beta:.2f}]"
        )

    def normalize_angle(self, angle: float) -> float:
        """Wrap angle to [-pi, pi] radians."""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def pose_callback(self, msg: Pose2D):
        # Update current robot pose
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta

        # Compute Cartesian errors
        dx = self.goal_x - self.x
        dy = self.goal_y - self.y
        dtheta = self.normalize_angle(self.goal_theta - self.theta)

        # Compute polar error coordinates (rho, alpha, beta)
        rho = math.hypot(dx, dy)

        cmd_vel_msg = Twist()

        # Phase 1: Drive towards target position if distance error > tolerance
        if rho > self.tolerance_dist:
            phi = math.atan2(dy, dx)
            alpha = self.normalize_angle(phi - self.theta)
            beta = self.normalize_angle(self.goal_theta - phi)

            # State feedback control law (Equations 1 & 2)
            v = self.k_rho * rho
            w = self.k_alpha * alpha + self.k_beta * beta

            # Velocity saturation limits
            v = max(0.0, min(v, self.v_max))
            w = max(-self.w_max, min(w, self.w_max))

            cmd_vel_msg.linear.x = float(v)
            cmd_vel_msg.angular.z = float(w)

        # Phase 2: In position, correct remaining orientation error
        elif abs(dtheta) > self.tolerance_theta:
            cmd_vel_msg.linear.x = 0.0
            # Proportional rotation in place
            w = 1.0 * dtheta
            w = max(-self.w_max, min(w, self.w_max))
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
    node = PoseController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
