#!/usr/bin/env python3
"""Lab 6 starter: pick one block, then stack three blocks."""

import threading
import time

import rclpy
from geometry_msgs.msg import Pose
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from pymoveit2 import MoveIt2
from pymoveit2.gripper_interface import GripperInterface

try:
    # Works when installed as a package module.
    from .gripper_runtime import GripperCommandRunner, GripperRuntimeConfig
except ImportError:
    # Works when run directly from this folder.
    from gripper_runtime import GripperCommandRunner, GripperRuntimeConfig


def make_pose(x, y, z, qx, qy, qz, qw) -> Pose:
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.x = qx
    pose.orientation.y = qy
    pose.orientation.z = qz
    pose.orientation.w = qw
    return pose


class PickAndPlaceNode(Node):
    def __init__(self):
        super().__init__("pick_and_place")
        self.declare_parameter("task", "pick_place_one")

        self.moveit2 = MoveIt2(
            node=self,
            joint_names=["joint_1", "joint_2", "joint_3", "joint_4", "joint_5", "joint_6"],
            base_link_name="base_link",
            end_effector_name="end_effector_link",
            group_name="arm",
        )

        try:
            self.gripper = GripperInterface(
                node=self,
                gripper_joint_names=["right_finger_bottom_joint"],
                open_gripper_joint_positions=[0.80],
                closed_gripper_joint_positions=[0.01],
                gripper_group_name="gripper",
                gripper_command_action_name="/gen3_lite_2f_gripper_controller/gripper_cmd",
                ignore_new_calls_while_executing=True,
            )
        except Exception as error:
            self.get_logger().warn(f"GripperInterface initialization failed: {error}")
            self.gripper = None

        # Runtime robustness helper (kept outside the student flow).
        self.gripper_runtime = GripperCommandRunner(
            logger=self.get_logger(),
            config=GripperRuntimeConfig(),
        )

        table_z = -0.0001
        block_size = 0.04
        self.table_center_z = table_z - 0.05 / 2.0
        self.block_center_z = table_z + block_size / 2.0

        self.blocks_xyz = [
            (0.45, -0.08, self.block_center_z),
            (0.45, 0.00, self.block_center_z),
            (0.45, 0.08, self.block_center_z),
        ]
        self.approach_height = 0.32
        self.grasp_height = 0.19
        self.top_down_orientation = (-0.7071, 0.7071, 0.0, 0.0)

        self.j_home = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.j_retract = [0.40, 0.02, 2.27, -1.57, -0.84, 1.97]
        self.touch_links = [
            "end_effector_link",
            "right_finger_bottom_link",
            "left_finger_bottom_link",
        ]

    def move_to_joints(self, joint_positions):
        self.moveit2.move_to_configuration(joint_positions=joint_positions)
        self.moveit2.wait_until_executed()

    def move_to_pose(self, pose: Pose, cartesian: bool = False) -> bool:
        trajectory = self.moveit2.plan(
            pose=pose,
            cartesian=cartesian,
            max_step=0.005,
            cartesian_fraction_threshold=0.90 if cartesian else None,
        )
        if trajectory is None:
            self.get_logger().error("Planning failed.")
            return False

        self.moveit2.execute(trajectory)
        self.moveit2.wait_until_executed()
        return True

    def open_gripper(self):
        self.gripper_runtime.run_command(self.gripper, "open")

    def close_gripper(self):
        self.gripper_runtime.run_command(self.gripper, "close")

    def add_scene(self):
        self.get_logger().info("Adding table and blocks to planning scene.")
        self.moveit2.add_collision_box(
            id="table_top",
            size=(1.0, 1.0, 0.05),
            position=(0.0, 0.0, self.table_center_z),
            quat_xyzw=(0.0, 0.0, 0.0, 1.0),
            frame_id="base_link",
        )
        time.sleep(0.1)

        for index, (x, y, z) in enumerate(self.blocks_xyz, start=1):
            self.moveit2.add_collision_box(
                id=f"block_{index}",
                size=(0.04, 0.04, 0.04),
                position=(x, y, z),
                quat_xyzw=(0.0, 0.0, 0.0, 1.0),
                frame_id="base_link",
            )
            time.sleep(0.05)

        self.get_logger().info("Planning scene ready.")

    def pick_and_place_block(self, block_id: str, pick_xyz, place_xyz) -> bool:
        pre_pick = make_pose(
            pick_xyz[0], pick_xyz[1], self.approach_height, *self.top_down_orientation
        )
        pick = make_pose(
            pick_xyz[0], pick_xyz[1], self.grasp_height, *self.top_down_orientation
        )
        pre_place = make_pose(
            place_xyz[0], place_xyz[1], self.approach_height, *self.top_down_orientation
        )
        place = make_pose(
            place_xyz[0], place_xyz[1], place_xyz[2], *self.top_down_orientation
        )

        if not self.move_to_pose(pre_pick):
            return False
        if not self.move_to_pose(pick, cartesian=True):
            return False

        self.close_gripper()
        self.moveit2.attach_collision_object(block_id, "end_effector_link", self.touch_links)
        time.sleep(0.2)

        if not self.move_to_pose(pre_pick, cartesian=True):
            return False
        if not self.move_to_pose(pre_place):
            return False
        if not self.move_to_pose(place, cartesian=True):
            return False

        self.open_gripper()
        self.moveit2.detach_collision_object(block_id)
        time.sleep(0.2)

        return self.move_to_pose(pre_place, cartesian=True)

    def task_pick_place_one(self):
        self.get_logger().info("Starting one-block pick/place task.")

        self.move_to_joints(self.j_retract)
        self.open_gripper()
        self.pick_and_place_block("block_1", self.blocks_xyz[0], self.blocks_xyz[0])
        self.move_to_joints(self.j_retract)
        self.get_logger().info("Task complete.")

    def task_stack_three(self):
        """
        Student task: stack all 3 blocks.
        Edit only stack_x and stack_y below.
        """
        self.get_logger().info("Starting stack-three task.")
        self.move_to_joints(self.j_retract)
        self.open_gripper()

        # STUDENT EDIT START
        # Choose where to build the stack (x, y in base_link frame).
        stack_x = 0.55
        stack_y = 0.00
        # STUDENT EDIT END

        stack_targets = [
            (stack_x, stack_y, self.grasp_height),
            (stack_x, stack_y, self.grasp_height + self.block_size),
            (stack_x, stack_y, self.grasp_height + 2.0 * self.block_size),
        ]

        block_ids = ["block_1", "block_2", "block_3"]
        for index, block_id in enumerate(block_ids):
            pick_xyz = self.blocks_xyz[index]
            place_xyz = stack_targets[index]
            if not self.pick_and_place_block(block_id, pick_xyz, place_xyz):
                self.get_logger().error(f"Failed while handling {block_id}.")
                self.move_to_joints(self.j_retract)
                return

        self.move_to_joints(self.j_retract)
        self.get_logger().info("Stack-three task complete.")

    def task_home(self):
        self.move_to_joints(self.j_home)

    def task_retract(self):
        self.move_to_joints(self.j_retract)

    def task_add_scene(self):
        self.add_scene()


def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlaceNode()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    threading.Thread(target=executor.spin, daemon=True).start()

    task = node.get_parameter("task").get_parameter_value().string_value
    node.get_logger().info(f"Executing task: '{task}'")

    try:
        if task == "home":
            node.task_home()
        elif task == "retract":
            node.task_retract()
        elif task == "add_scene":
            node.task_add_scene()
        elif task == "pick_place_one":
            node.task_pick_place_one()
        elif task == "stack_three":
            node.task_stack_three()
        else:
            node.get_logger().warn(
                f"Unknown task '{task}'. Valid tasks: home, retract, add_scene, pick_place_one, stack_three"
            )
    finally:
        time.sleep(1.0)
        rclpy.shutdown()


if __name__ == "__main__":
    main()
