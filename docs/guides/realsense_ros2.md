# Intel RealSense D435i and D421 in ROS 2

Use the `realsense2_camera` driver to run an Intel RealSense D435, D435i, or D421 depth camera in ROS 2 Jazzy. You can view its images and point cloud, then record them for playback on your Duke VM.

!!! warning "Draft: tested on Windows only"
    On 2026-11-12 these steps were run with a D435i and a D421 on a Windows 11 laptop through WSL2 and `usbipd-win`, in the course's `kinova-jazzy` image. Over that connection the depth image had to be reduced to 480 x 270 (see [Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win)). The steps have not yet been run on a lab computer or a Raspberry Pi. If a step does not behave as described, post the command and its full output on Ed Discussions.

The D435 has a color camera and a stereo depth camera. The D435i adds an IMU (accelerometer and gyroscope). The D421 is a bare depth module: it has the stereo depth camera and infrared images, but no color camera and no IMU. Steps that use the color image or align depth to it need a color camera, and the IMU section is for the D435i only. [The D421](#the-d421) lists the D421's launch options and topics.

## Where the camera plugs in

Course VMs have no USB access, so a camera cannot be connected to your VM. Plug the RealSense into a lab computer (Ubuntu with Docker) or a Raspberry Pi 5 and run the driver there. To work with the data on your VM, record a bag on the computer the camera is plugged into, copy the bag to your VM, and play it back there. [Section 7](#7-record-a-bag-and-play-it-on-your-vm) shows how.

## What you need

- A RealSense D435, D435i, or D421.
- A USB 3 cable. The camera has a USB-C port. Many USB-C cables (phone charging cables, for example) carry only USB 2 data, and the camera runs with reduced frame rates and resolutions over USB 2. Use the cable that came with the camera when you can.
- A USB 3 port on the computer. These are usually blue inside or marked `SS`. On a Raspberry Pi 5, use one of the two blue ports.
- A lab computer with Docker, or a Raspberry Pi 5 with Docker.
- The course image `ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest`. Use `turtlebot4-jazzy-latest` instead if you want to run the Lab 9 hazard monitor ([Section 8](#8-use-the-camera-with-the-lab-9-hazard-monitor)).

## 1. One-time host setup: udev rules

Intel's installation instructions add udev rules on the host. The rules set permissions on the camera's USB and IMU device files so that programs can open them. Course staff install them once on each lab computer or Pi; this step needs `sudo`. If you are using a lab computer, ask a TA whether it has been done.

```bash
sudo curl -fsSL -o /etc/udev/rules.d/99-realsense-libusb.rules \
  https://raw.githubusercontent.com/IntelRealSense/librealsense/v2.58.4/config/99-realsense-libusb.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

These commands install `99-realsense-libusb.rules`, the rules file that Intel's `setup_udev_rules.sh` script installs, and reload the rules. The file comes from the librealsense version that the ROS driver uses (2.58.4). Unplug the camera and plug it back in afterward.

## 2. Check the camera on the host

Plug in the camera, then run these in a terminal on the lab computer or Pi (not inside a container):

```bash
lsusb | grep 8086
lsusb -t
```

The first command should print one line with ID `8086:0b07` for a D435, `8086:0b3a` for a D435i, or `8086:1155` for a D421. If it prints nothing, the camera is not listed: try another cable or port.

In the `lsusb -t` tree, find the lines with `Driver=uvcvideo` for the camera. The number at the end of each line is the link speed: `5000M` (or higher) means USB 3, and `480M` means USB 2. If you see `480M`, change the cable or port before going further.

## 3. Start the container with the camera

On the lab computer, open a terminal and run:

```bash
xhost +local:docker
docker run --rm -it \
  --name realsense \
  --net=host \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  -v /dev:/dev \
  --device-cgroup-rule "c 81:* rmw" \
  --device-cgroup-rule "c 189:* rmw" \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest
```

| Flag | Purpose |
|------|---------|
| `-v /dev:/dev` | Makes the host's device files visible in the container. The RealSense uses several device files, and the camera disconnects and reconnects when it resets, which creates them again. Mounting all of `/dev` keeps the new ones visible. |
| `--device-cgroup-rule "c 81:* rmw"` | Allows the container to use video devices (`/dev/video*`). |
| `--device-cgroup-rule "c 189:* rmw"` | Allows the container to use USB devices (`/dev/bus/usb/*`). |
| `--gpus all` | Lets RViz use the GPU, which helps when drawing point clouds. If `docker run` reports `could not select device driver`, run the command again without this line. |
| `-v ~/workspaces:/root/workspaces` | Mounts the host's `~/workspaces` folder in the container, so bags you record there stay after the container exits. |
| `-e DISPLAY=$DISPLAY` and `-v /tmp/.X11-unix:...` | Let RViz and other windows open on the host's screen. |

The `-v /dev:/dev` line and the two `--device-cgroup-rule` lines are the method in Intel's librealsense Docker instructions.

On a Raspberry Pi 5, use the ARM64 course image named in your project instructions in place of `base-jazzy-latest`, and leave out `--gpus all`.

## 4. Install the driver and check the camera

Check whether the image already has the driver:

```bash
ros2 pkg prefix realsense2_camera
```

If it prints `/opt/ros/jazzy`, skip the install. If it prints `Package 'realsense2_camera' not found`, install the driver from the ROS package repository:

```bash
apt-get update && apt-get install -y ros-jazzy-realsense2-camera
```

This also installs `librealsense2`, Intel's camera library, and its tools. You are root inside the container, so `sudo` is not needed. The `--rm` flag deletes the container when you exit, including packages you installed in it. In each new container, check whether the driver is installed before running the install command.

Then check whether the camera is detected inside the container:

```bash
rs-enumerate-devices -s
```

It should print one line with the camera's name, serial number, and firmware version. `No device detected. Is it plugged in?` means the tool did not detect a camera inside the container; see [Common problems](#common-problems). Without the `-s`, the command also lists every stream profile (resolution, frame rate, and format) the camera supports, which you need for Section 5.

`realsense-viewer`, Intel's camera viewer, is installed too. Use it to check whether the camera's streams work without ROS. Close it before starting the ROS driver so the programs do not try to open the same streams.

## 5. Run the driver

The basic launch:

```bash
ros2 launch realsense2_camera rs_launch.py
```

The first log lines show the driver and library versions (`RealSense ROS v4.58.4`, `Built with LibRealSense v2.58.4`). For models with a color camera, the driver publishes the color image and the depth image under `/camera/camera/` with the defaults.

A launch that also aligns depth to the color image and publishes a point cloud, with explicit image sizes:

```bash
ros2 launch realsense2_camera rs_launch.py \
  rgb_camera.color_profile:=640x480x30 \
  depth_module.depth_profile:=848x480x30 \
  align_depth.enable:=true \
  pointcloud.enable:=true
```

Launch arguments (`ros2 launch realsense2_camera rs_launch.py --show-args` lists all of them):

| Argument | Default | Meaning |
|----------|---------|---------|
| `rgb_camera.color_profile` | `0,0,0` (camera default) | Color width x height x frame rate, such as `640x480x30` |
| `depth_module.depth_profile` | `0,0,0` (camera default) | Depth width x height x frame rate, such as `848x480x30` |
| `align_depth.enable` | `false` | Publish a depth image aligned to the color image |
| `pointcloud.enable` | `false` | Publish a point cloud |
| `enable_color`, `enable_depth` | `true` | Turn the color or depth stream on or off |
| `enable_gyro`, `enable_accel` | `false` | IMU streams (D435i only) |
| `unite_imu_method` | `0` | `0` no combined IMU topic, `1` copy, `2` linear interpolation |
| `initial_reset` | `false` | Reset the camera before starting it |
| `camera_namespace`, `camera_name` | `camera`, `camera` | The two parts of the topic prefix `/camera/camera/` |

Choose a profile the camera supports for that stream from the list printed by `rs-enumerate-devices`. If the driver prints a warning about an unsupported profile, check the profile and the image size and frame rate in use.

### Topics

With `align_depth.enable:=true` and `pointcloud.enable:=true`, the main topics are:

| Topic | Type | Contents |
|-------|------|----------|
| `/camera/camera/color/image_raw` | `sensor_msgs/msg/Image` | Color image, `rgb8` |
| `/camera/camera/color/camera_info` | `sensor_msgs/msg/CameraInfo` | Color camera calibration (from the camera's factory calibration) |
| `/camera/camera/depth/image_rect_raw` | `sensor_msgs/msg/Image` | Depth image, `16UC1`, in millimeters; `0` means no reading |
| `/camera/camera/depth/camera_info` | `sensor_msgs/msg/CameraInfo` | Depth camera calibration |
| `/camera/camera/aligned_depth_to_color/image_raw` | `sensor_msgs/msg/Image` | Depth resampled to the color camera's view and size, so pixel (u, v) in it matches pixel (u, v) in the color image |
| `/camera/camera/aligned_depth_to_color/camera_info` | `sensor_msgs/msg/CameraInfo` | Calibration for the aligned depth image |
| `/camera/camera/depth/color/points` | `sensor_msgs/msg/PointCloud2` | Point cloud with color |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | Transforms between the camera's frames |

The driver also publishes `metadata` topics beside each image, `/camera/camera/extrinsics/depth_to_color`, and `compressed`, `compressedDepth`, `theora`, and `zstd` copies of each image from the image transport plugins in the course image. These additional topics are not needed for the steps below.

Check that images are arriving with `ros2 topic hz /camera/camera/color/camera_info` in a second terminal (open one with `docker exec -it realsense bash` on the host). The driver publishes one `camera_info` message with each image, so its rate is the image rate; in testing, the color, depth, and aligned depth `camera_info` topics each ran at 30.0 Hz. `ros2 topic hz` on the image topic itself can report less than the real rate when it cannot keep up with full-size images.

The camera's coordinate frames are `camera_link` (the camera body), `camera_color_optical_frame`, and `camera_depth_optical_frame`. Optical frames follow the image convention: z forward out of the lens, x to the right, y down.

### IMU (D435i only)

```bash
ros2 launch realsense2_camera rs_launch.py enable_gyro:=true enable_accel:=true unite_imu_method:=2
```

This adds `/camera/camera/gyro/sample` and `/camera/camera/accel/sample`, each with only its own fields filled in, and `/camera/camera/imu` (`sensor_msgs/msg/Imu`) with both, published at the gyroscope rate.

In testing with the container from Section 3, the driver printed `HID Motion Sensor Failure (continuing as partial device)` and `IMU is disabled` at startup, and the color and depth streams worked without the IMU. See [Common problems](#common-problems).

### The D421

The D421 has no color camera, so turn the color stream off and the left infrared stream on:

```bash
ros2 launch realsense2_camera rs_launch.py enable_color:=false enable_infra1:=true
```

Its main topics are:

| Topic | Type | Contents |
|-------|------|----------|
| `/camera/camera/depth/image_rect_raw` | `sensor_msgs/msg/Image` | Depth image, `16UC1`, in millimeters; `0` means no reading |
| `/camera/camera/depth/camera_info` | `sensor_msgs/msg/CameraInfo` | Depth camera calibration |
| `/camera/camera/infra1/image_rect_raw` | `sensor_msgs/msg/Image` | Left infrared image, `mono8` |
| `/camera/camera/infra1/camera_info` | `sensor_msgs/msg/CameraInfo` | Left infrared camera calibration |

The depth image is computed from the left infrared camera's viewpoint, so pixel (u, v) in the infrared image matches pixel (u, v) in the depth image when both have the same size. `align_depth.enable` has no color image to align to. The infrared image shows a pattern of dots: the camera's projector puts them on the scene so that it can measure depth on plain surfaces. A glossy surface facing the camera, such as a whiteboard, can reflect the projector straight back and leave a hole in the depth image there.

In testing, the driver version in this guide (4.58.4, with librealsense 2.58.4) detected and streamed from the D421 (firmware 5.16.3) with the launch options above.

## 6. View the images and point cloud

**rqt_image_view.** Run `ros2 run rqt_image_view rqt_image_view` and choose a topic from the drop-down list, such as `/camera/camera/color/image_raw` or `/camera/camera/depth/image_rect_raw`. Depth images can look almost black, because the values are millimeters stored in 16-bit pixels.

**RViz with the driver's configuration.** The driver package includes an RViz configuration that shows the point cloud and the images:

```bash
rviz2 -d /opt/ros/jazzy/share/realsense2_camera/launch/default.rviz
```

Its Fixed Frame is `camera_depth_optical_frame`. The point cloud appears only if you launched with `pointcloud.enable:=true`. The infrared image panels stay empty because infrared streams are off by default.

**RViz from scratch.** Run `rviz2`. Set **Global Options > Fixed Frame** to `camera_link`. Click **Add**, open the **By topic** tab, and choose **PointCloud2** under `/camera/camera/depth/color/points`. Add **Image** displays for the image topics the same way.

## 7. Record a bag and play it on your VM

**Record on the lab computer.** Launch with `align_depth.enable:=true`, then in a second container terminal run:

```bash
cd ~/workspaces
ros2 bag record -o realsense_test \
  /camera/camera/color/image_raw /camera/camera/color/camera_info \
  /camera/camera/aligned_depth_to_color/image_raw /camera/camera/aligned_depth_to_color/camera_info \
  /tf_static
```

Press `Ctrl+C` to stop recording. The bag is the folder `~/workspaces/realsense_test`, which is also on the host because of the `-v ~/workspaces:/root/workspaces` mount. `ros2 bag info realsense_test` shows what it contains.

At 640 x 480 and 30 frames per second, the color and aligned depth images contain about 46 MB of pixel data per second, or about 2.8 GB per minute; bag storage also includes message and file overhead. Keep recordings short to limit storage use, and omit the point cloud topic to reduce the bag size. On the VM, RViz can draw a point cloud from the recorded depth and color images (see below).

**Copy the bag to your VM.** In a host terminal on the lab computer (not in the container), run the following, with your NetID and your VM's host name:

```bash
scp -r ~/workspaces/realsense_test NETID@YOUR-VM.vm.duke.edu:~/workspaces/
```

If `scp` reports `Permission denied` for files inside the bag folder, check whether the container created them as root. If so, change the ownership with `sudo chown -R $USER:$USER ~/workspaces/realsense_test` and copy again.

**Play it on your VM.** Start the course container on your VM as usual, then run:

```bash
ros2 bag play ~/workspaces/realsense_test
```

Add `--loop` to repeat the recording until you press `Ctrl+C`. While it plays, `rqt_image_view` shows the recorded images. To see the scene in 3D in RViz:

1. Run `rviz2` and set **Fixed Frame** to `camera_color_optical_frame`.
2. Click **Add**, and on the **By display type** tab choose **DepthCloud**.
3. In the DepthCloud display, set **Depth Map Topic** to `/camera/camera/aligned_depth_to_color/image_raw` and **Color Image Topic** to `/camera/camera/color/image_raw`.

## 8. Use the camera with the Lab 9 hazard monitor

The Lab 9 starter repository's `README.md` has a section, "Optional: using your sensor code in your project", on running `hazard_monitor` with a real camera. The monitor converts the RealSense's `rgb8` color images and its `16UC1` depth images in millimeters, so your functions receive RGB pixels and depth in meters. Use the `turtlebot4-jazzy-latest` image for this, since the monitor uses TurtleBot 4 message packages that `base-jazzy-latest` does not include.

With the driver running with `align_depth.enable:=true`, or a bag from Section 7 playing, run this from the root of your Lab 9 repository after building the workspace:

```bash
ros2 run lab09_sensors hazard_monitor --ros-args \
  -p image_topic:=/camera/camera/color/image_raw \
  -p depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  -p camera_info_topic:=/camera/camera/aligned_depth_to_color/camera_info \
  -p camera_height:=0.30
```

Replace `0.30` with the height of your camera above the floor, in meters, and set `use: true` in `thresholds.yaml` only for the sensors you have.

## Running on Windows with WSL2 and usbipd-win

!!! warning "Tested on one laptop"
    This section was tested on one staff Windows 11 laptop with one D435i and one D421. Results on other computers may differ.

On Windows, Docker Desktop runs Linux containers inside WSL2, and WSL2 cannot see USB devices until you attach them with [usbipd-win](https://github.com/dorssel/usbipd-win). Install usbipd-win and attach the camera as in steps 1 to 5 of the webcam guide's [Running on Windows](usb_webcam_ros2.md#running-on-windows-with-wsl2-and-usbipd-win) section. The RealSense appears in `usbipd list` as `Intel(R) RealSense(TM) Depth Camera 435i` or `... Depth Camera 421`. On the test laptop, the plain `usbipd bind` (without `--force`) was enough for both cameras, despite the `CsDeviceControl` warning.

Three differences from a lab computer:

1. **Load the Linux camera driver.** On the test laptop, the WSL2 kernel (6.18.58) did not load its USB video driver (`uvcvideo`) when the camera was attached. The container then has no `/dev/video*` entries, and the ROS driver prints `No RealSense devices were found!`. If the container has no `/dev/video*` entries, load the driver in PowerShell. In testing it had to be loaded again each time Docker Desktop's WSL2 system restarted:

    ```powershell
    docker run --rm --privileged -v /lib/modules:/lib/modules alpine sh -c "apk add -q kmod && modprobe uvcvideo"
    ```

    In this test, loading the driver made the camera appear as six entries, `/dev/video0` to `/dev/video5`.

2. **Use a smaller depth image.** Over this connection, depth images of 848 x 480 and 640 x 480 arrived 26 to 34% complete, and the driver dropped them with `Incomplete video frame detected!`. This happened at 15 and at 30 frames per second. Depth at 480 x 270 arrived complete at 30 frames per second, with the color image at 640 x 480 running too:

    ```bash
    ros2 launch realsense2_camera rs_launch.py depth_module.depth_profile:=480x270x30 rgb_camera.color_profile:=640x480x30 align_depth.enable:=true
    ```

    For a D421, use `depth_module.depth_profile:=480x270x30 depth_module.infra_profile:=480x270x30` with the options from [The D421](#the-d421). The aligned depth image of a D435i has the color image's size, 640 x 480, even when the depth stream is 480 x 270.

3. **Start the container from PowerShell.** Use the command from Section 3 with these changes: replace each `\` at the end of a line with a backtick, replace the two display lines with `-e DISPLAY=:0` and `-v /run/desktop/mnt/host/wslg/.X11-unix:/tmp/.X11-unix:ro`, write the workspace mount as `-v "${HOME}/workspaces:/root/workspaces"`, and leave out `xhost`. The `-v /dev:/dev` line and both `--device-cgroup-rule` lines stay as they are.

In testing, `usbipd attach` failed with `There is no WSL 2 distribution running` after Docker Desktop's WSL2 system had stopped. Start any container (for example `docker run --rm alpine true`) and attach again. Starting the container starts the WSL2 system again, so load `uvcvideo` again (step 1).

## Common problems

**`Package 'realsense2_camera' not found`.** The driver is not installed in this container. Run the install in Section 4.

**`No RealSense devices were found!`, repeated every few seconds.** The driver has not detected the camera. Check, in order:

1. On the host, `lsusb | grep 8086` lists the camera (Section 2). If not, reseat the cable or try another cable or port. On Windows, check that `usbipd list` shows the camera as `Attached` and that `uvcvideo` is loaded ([Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win), step 1).
2. The container was started with `-v /dev:/dev` and both `--device-cgroup-rule` lines (Section 3).
3. No other program is using the camera, such as `realsense-viewer` or a second copy of the driver.
4. `rs-enumerate-devices -s` in the container finds the camera. If it does but the driver does not, stop the driver and start it again.

**A warning that the device is connected over USB 2 (for example, `is connected using a 2.1 port`).** The connection is running at USB 2 speed, which limits the available profiles. Check `lsusb -t` (Section 2) and change the cable or port.

**The driver starts, but no images arrive, or they stop after a while.** Stop the driver, unplug the camera for a few seconds, plug it back in, and launch again with `initial_reset:=true` added. If it keeps happening, try a shorter cable or a different USB 3 port, and avoid USB hubs.

**`Incomplete video frame detected!`, repeated, and no depth images.** The depth frames are not arriving whole. On Windows, use a 480 x 270 depth profile ([Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win), step 2). On a lab computer, check the USB 3 connection (Section 2).

**The image size or frame rate is not what you asked for.** Check the driver's log for a warning about an unsupported profile and pick a supported profile from `rs-enumerate-devices`.

**No point cloud in RViz.** Check that you launched with `pointcloud.enable:=true` and that `ros2 topic hz /camera/camera/depth/color/points` reports messages. If it does, set the Fixed Frame to `camera_link`. If RViz still shows nothing, expand the PointCloud2 display's **Topic** settings and change **Reliability Policy** to **Best Effort**.

**IMU errors on a D435i.** In testing on Windows, the driver printed `HID Motion Sensor Failure` and `IMU is disabled` in the container from Section 3, and the fix has not been confirmed. If the driver reports this or other errors for the gyro or accelerometer, try starting the container with `--privileged` in place of the two `--device-cgroup-rule` lines (keep `-v /dev:/dev`), and ask a TA whether the udev rules from Section 1 are installed.

**No window opens (`could not connect to display`).** Run `xhost +local:docker` on the host and start the container again with the `DISPLAY` and `/tmp/.X11-unix` options from Section 3.

**Your VM does not see the camera's topics.** With `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`, automatic topic discovery is limited to the lab computer, so the VM does not automatically discover the camera's topics. Record a bag and play it on the VM (Section 7).

??? note "To verify on hardware (staff checklist; remove when done)"
    Checked without a camera on 2026-11-03: `ros-jazzy-realsense2-camera` 4.58.4 with `ros-jazzy-librealsense2` 2.58.4 installs with `apt-get` in the published `turtlebot4-jazzy-latest` image and is absent from it; arm64 builds of both exist in the ROS apt repository; every launch argument name and default in the table (`rs_launch.py --show-args`); the startup version lines and the `No RealSense devices were found!` and `Package ... not found` messages; `rs-enumerate-devices` (its `-s` option and its no-device message) and `realsense-viewer` are installed by the package; `default.rviz` path, Fixed Frame, and topics; the RViz DepthCloud display exists in the image; `librealsense2` in the ROS package uses the V4L2 backend; the udev rules file at tag v2.58.4 lists product IDs `0b07` (D435) and `0b3a` (D435i); `hazard_monitor` handles `rgb8` and `16UC1`. Topic names, frame names, and IMU behavior come from the upstream README and strings in the driver binary.

    Checked with cameras on 2026-11-12: a D435i (FW 5.17.0.9) and a D421 (FW 5.16.3, product ID `0x1155`) on the staff Windows 11 laptop, WSL2 kernel 6.18.58, `usbipd-win` plain `bind`, Docker Desktop 29.9.3, image `kinova-jazzy-20261015` with `ros-jazzy-realsense2-camera` 4.58.4 installed by `apt-get`. The container was started from Git Bash with `-v /dev:/dev` and both cgroup rules, not interactively and not from PowerShell. Confirmed:

    - [x] `uvcvideo` had to be loaded by hand (`modprobe` in a privileged container with `/lib/modules` mounted); without it, no `/dev/video*` and `No RealSense devices were found!`. With it, `/dev/video0` to `/dev/video5`.
    - [x] Driver finds both cameras with the cgroup-rule container (`Device USB type: 3.2`). `rs-enumerate-devices -s` printed `No device detected` before `uvcvideo` was loaded; not rerun after.
    - [x] D435i: depth `848x480x30` and `640x480x15` frames arrive 26 to 34% complete over usbipd (`Incomplete video frame detected!`, `Frame Corrupted`); `480x270x30` complete. With depth `480x270x30`, color `640x480x30` and `align_depth`: color, depth, and aligned depth `camera_info` each at 30.0 Hz. Color `rgb8`, aligned depth `16UC1`, frame `camera_color_optical_frame`.
    - [x] Topic list with `align_depth` (no point cloud): the topics in the table plus `metadata`, `extrinsics/depth_to_color`, and the `compressed`, `compressedDepth`, `theora`, `zstd` transports.
    - [x] D421 with `enable_color:=false enable_infra1:=true` at `480x270x30`: depth and `infra1` (`mono8`) at 30 Hz.
    - [x] Depth check against a whiteboard measured at about 0.508 m: D435i median 0.489 m (0.482 and 0.497 m at two pixels); D421 median 0.492 m with the camera somewhat closer. The D421 had a depth hole at the image center from the projector's reflection.
    - [x] D435i IMU: `HID Motion Sensor Failure (continuing as partial device)`, `IMU is disabled` with the cgroup-rule container.
    - [x] `usbipd attach` failed with `There is no WSL 2 distribution running` after Docker Desktop's WSL2 system had stopped; starting a container fixed it, and `uvcvideo` had to be loaded again.

    Still to confirm with a camera:

    - [ ] Everything on a lab computer with native USB, especially the `848x480x30` depth profile.
    - [ ] `lsusb` IDs and the `lsusb -t` speed reading on a Linux host for D435, D435i, and D421.
    - [ ] Whether the udev rules are needed at all when the driver runs as root in the container.
    - [ ] Terminal (`-it`, `Ctrl+C`) still works with the host's `/dev` mounted; the PowerShell form of the Section 3 command.
    - [ ] `rs-enumerate-devices -s` output format with a camera, and whether the full output shows the USB type.
    - [ ] The topic list with `pointcloud` enabled.
    - [ ] The warning text for an unsupported profile.
    - [ ] Text of the USB 2 warning.
    - [ ] `initial_reset:=true` behavior inside the container (camera re-enumerates and is found again).
    - [ ] `default.rviz` shows the point cloud; RViz PointCloud2 from scratch with Fixed Frame `camera_link`; whether the Best Effort change is ever needed.
    - [ ] D435i IMU: whether `--privileged` (or mounting the IMU's `hidraw` device) fixes the `HID Motion Sensor Failure`.
    - [ ] Recording rate of about 46 MB/s; whether lab computer disks keep up.
    - [ ] VM playback: DepthCloud display with Fixed Frame `camera_color_optical_frame`; `/tf_static` playback.
    - [ ] Lab 9 `hazard_monitor` with the aligned depth topics, live and from a bag.
    - [ ] Raspberry Pi 5: ARM64 image name, power from the Pi's USB 3 port, achievable frame rates.
    - [ ] Optional check that needs no camera: Intel's `d435i_sample_data.zip` (472 MB) can be played through the driver with `rosbag_filename:=...` to confirm topic names, alignment, and the point cloud.

## References

- `realsense2_camera` ROS 2 wrapper documentation: [github.com/IntelRealSense/realsense-ros](https://github.com/IntelRealSense/realsense-ros/tree/ros2-master)
- librealsense Linux installation and udev rules: [installation.md](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md) and [distribution_linux.md](https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md)
- librealsense in Docker: [scripts/Docker/readme.md](https://github.com/IntelRealSense/librealsense/blob/master/scripts/Docker/readme.md)
- `rqt_image_view`: [github.com/ros-visualization/rqt_image_view](https://github.com/ros-visualization/rqt_image_view)
- Recording and playing back data (ROS 2 Jazzy tutorial): [docs.ros.org](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html)
- `docker run --device-cgroup-rule`: [docs.docker.com](https://docs.docker.com/reference/cli/docker/container/run/#device-cgroup-rule)
