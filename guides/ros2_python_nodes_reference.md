# ROS 2 Python Nodes Reference

Use this page when you are writing beginner-to-intermediate ROS 2 nodes in Python with `rclpy`.

This guide is intentionally focused on the patterns students usually need first: node setup, publishers, subscribers, timers, messages, logging, and common package/build mistakes.

## Main function pattern

Every node file needs a `main()` function that handles initialization, spinning, and cleanup.

```python
def main(args=None):
    rclpy.init(args=args)
    my_node = PubNodeA()   # Replace with your class name
    rclpy.spin(my_node)
    my_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
```

## Publisher

Method:

```python
self.create_publisher(msg_type, topic_name, queue_size)
```

- `msg_type` is the message type, such as `String`
- `topic_name` is the topic string, such as `"/topic_a_to_b"`
- `queue_size` is the buffer depth, and `10` is a good default for these labs

Example:

```python
self.pub = self.create_publisher(String, "/topic_a_to_b", 10)
self.pub.publish(msg)
```

## Subscriber

Method:

```python
self.create_subscription(msg_type, topic_name, callback, queue_size)
```

- The callback runs whenever a message arrives
- The callback must accept exactly one argument: the incoming message

Example:

```python
self.sub = self.create_subscription(String, "/topic_a_to_b", self._on_msg, 10)

def _on_msg(self, msg):
    self.get_logger().info(f'Received: "{msg.data}"')
```

## Timer

Method:

```python
self.create_timer(period_seconds, callback)
```

- Runs the callback periodically
- The timer callback takes no arguments

Example:

```python
self.timer = self.create_timer(2.0, self._tick)

def _tick(self):
    self.get_logger().info("Timer fired!")
```

## Messages

Lab 04 uses the `String` message type:

```python
from std_msgs.msg import String

msg = String()
msg.data = "your content here"
```

## Logging

Inside a node, use the built-in logger:

```python
self.get_logger().info("Plain message")
self.get_logger().info(f"Value is: {my_var}")
```

## Common problems

- `ros2 run` says the command does not exist:
  Check the `setup.py` entry point, rebuild the workspace, and source `install/setup.bash`.
- Code changes do not show up:
  Rebuild if you did not use `--symlink-install`, and always rebuild after adding a new file.
- `ImportError` when running a node:
  Source the workspace again and confirm the package was rebuilt after adding files.
- Changes to `setup.py` or `package.xml` do not take effect:
  Rebuild, then re-source in a fresh terminal.
- No messages on a topic:
  Confirm the topic name matches exactly and use `ros2 topic list` or `ros2 topic echo` to inspect the graph.
- Node runs but prints nothing:
  Check logger calls and confirm subscriber callback signatures are correct.
- Multiple nodes appear to collide:
  Give each node a unique name in `super().__init__()`.

## Helpful cleanup

If you accidentally committed build artifacts:

```bash
git rm -r --cached build/ install/ log/
git commit -m "Remove build artifacts"
git push
```

## Related docs

- [Quick reference](quick_reference.md)
- [Troubleshooting](../troubleshooting.md)
