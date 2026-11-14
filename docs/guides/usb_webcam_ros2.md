# USB Webcam in ROS 2

This guide shows how to publish images from a USB webcam in ROS 2 Jazzy with the `v4l2_camera` driver, view them, and record them so you can work with them on your Duke VM.

!!! warning "Draft: tested on Windows only"
    On 2026-11-03 these steps were run with an Amazon Basics webcam (USB ID `208e:2cc9`, which reports itself as `USB 2.0 Camera`) on a Windows 11 laptop through WSL2 and `usbipd-win` 5.3.0, with Docker Desktop 29.9.2 and the published `base-jazzy-latest` and `turtlebot4-jazzy-latest` images. On that laptop `v4l2_camera` produced incomplete images (see [Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win)), and the camera steps of Sections 5 to 8 were tested with `usb_cam`. The steps have not yet been run on a lab computer or a Raspberry Pi. If a step does not behave as described, post the command and its full output on Ed Discussions.

## Where the camera plugs in

Course VMs have no USB access, so a camera cannot be connected to your VM. Plug the webcam into a lab computer (Ubuntu with Docker) or a Raspberry Pi 5 and run the driver there. To work with the images on your VM, record a bag on the computer the camera is plugged into, copy the bag to your VM, and play it back there. [Section 7](#7-record-a-bag-and-play-it-on-your-vm) shows how. If you have your own Windows computer with Docker Desktop, see [Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win).

## What you need

- A USB webcam. Most webcams use the standard USB Video Class (UVC) and work with this driver. The driver's documentation lists the Logitech C920 and BRIO 4K Pro as tested.
- A lab computer with Docker, or a Raspberry Pi 5 with Docker.
- The course image `ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest`. Use `turtlebot4-jazzy-latest` instead if you want to run the Lab 9 hazard monitor ([Section 8](#8-use-the-camera-with-the-lab-9-hazard-monitor)).

This guide does not cover the Raspberry Pi Camera Module (the ribbon-cable camera). That camera uses a different driver stack that `v4l2_camera` does not support.

## 1. Check the camera on the host

Plug in the webcam, then run these in a terminal on the lab computer or Pi (not inside a container):

```bash
ls /dev/video*
lsusb
```

`ls` should list at least `/dev/video0`. Many webcams create two entries, such as `/dev/video0` and `/dev/video1`; the first one is the image stream and the second carries metadata. `lsusb` should list a line for the camera. Some cameras show their maker's name there; others show only a generic name such as `USB 2.0 Camera`.

If the computer already has another camera (a laptop's built-in camera, for example), your webcam may be `/dev/video2` or higher. Unplug the webcam, run `ls /dev/video*` again, and compare the two lists to find which entries belong to it.

## 2. Start the container with the camera

On the lab computer, open a terminal and run:

```bash
xhost +local:docker
docker run --rm -it \
  --name webcam \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  --device /dev/video0 \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest
```

| Flag | Purpose |
|------|---------|
| `--device /dev/video0` | Gives the container access to the camera. If your camera is `/dev/video2`, write `--device /dev/video2` here and use the same name for `video_device` in Section 5. |
| `-v ~/workspaces:/root/workspaces` | Mounts the host's `~/workspaces` folder in the container, so bags you record there stay after the container exits. |
| `-e DISPLAY=$DISPLAY` and `-v /tmp/.X11-unix:...` | Let windows such as `rqt_image_view` and RViz open on the host's screen. `xhost +local:docker` allows the container to draw on it. |
| `-e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` | Limits ROS 2 discovery to this computer. |

The camera must be connected before you run this command. If it is not, `docker run` stops with `error gathering device information while adding custom device "/dev/video0": no such file or directory`.

On a Raspberry Pi 5, use the ARM64 course image named in your project instructions in place of `base-jazzy-latest`. The rest of the command is the same.

## 3. Check the camera inside the container

In the container terminal, run:

```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext
```

The first command lists the camera's name and the `/dev/video` entries the container can use. The second lists the pixel formats the camera offers and, for each format, the image sizes and frame rates. Look for the `YUYV` entries: the driver in this guide reads `YUYV`, `UYVY`, and `GREY` only. Many webcams also offer `MJPG` (Motion-JPEG), which this driver cannot read. If `--list-formats-ext` prints no formats, you may have selected the metadata entry. Start the container with the camera's other `/dev/video` entry and check its formats again.

## 4. Install the driver

Check whether the image already has the driver:

```bash
ros2 pkg prefix v4l2_camera
```

If it prints `/opt/ros/jazzy`, skip to Section 5. If it prints `Package not found`, install it:

```bash
apt-get update && apt-get install -y ros-jazzy-v4l2-camera
```

You are root inside the container, so `sudo` is not needed. The `--rm` flag deletes the container when you exit, including packages you installed in it. In each new container, check whether the driver is installed before running the install command. If the course image includes the driver, the check above prints `/opt/ros/jazzy`.

## 5. Run the driver

```bash
ros2 run v4l2_camera v4l2_camera_node --ros-args -p image_size:="[640,480]"
```

When it starts, the driver prints the camera's name, the pixel formats it offers, and its controls (brightness, contrast, and so on), then `Requesting format: 640x480 YUYV` and `Starting camera`. The following messages can appear without stopping the driver:

- `Image encoding not the same as requested output, performing possibly slow conversion: yuv422_yuy2 => rgb8`. The camera sends `YUYV` and the driver converts each frame to RGB.
- `Unable to open camera calibration file` and `Camera calibration file ... not found`. No calibration file exists for this camera yet; see `camera_info_url` below.
- Some cameras also print `Failed getting value for control ...: Permission denied` or `Control type not currently supported` for a control the driver cannot read.

Driver parameters (`ros2 param list /v4l2_camera` lists all of them, including the camera controls described below the table):

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `video_device` | `/dev/video0` | The camera's device path inside the container |
| `image_size` | `[640, 480]` | Width and height in pixels. Must be a size listed for the pixel format in Section 3 |
| `pixel_format` | `YUYV` | Format requested from the camera: `YUYV`, `UYVY`, or `GREY` |
| `output_encoding` | `rgb8` | Encoding of the published image, such as `rgb8`, `bgr8`, or `mono8` |
| `camera_frame_id` | `camera` | The `frame_id` written in each image header |
| `camera_info_url` | (empty) | Calibration file to load, such as `file:///root/workspaces/my_camera.yaml` |

The driver has no frame-rate parameter. The camera picks its frame rate for the format and size you request, and the frame rates listed in Section 3 show what to expect. Large `YUYV` sizes often run slowly; the webcam used to test this guide lists `YUYV` at 30 frames per second at 640 x 480, 10 at 1280 x 720, and 5 at 1920 x 1080. Start at 640 x 480.

The camera's controls also become parameters, named from the control's name in lower case with spaces replaced by underscores (`Brightness` becomes `brightness`). `ros2 param list /v4l2_camera` shows them.

Open a second terminal in the same container with `docker exec -it webcam bash` (run on the host) and check the topics:

```bash
ros2 topic list
ros2 topic hz /camera_info
```

The topics are:

| Topic | Type | Contents |
|-------|------|----------|
| `/image_raw` | `sensor_msgs/msg/Image` | The image |
| `/camera_info` | `sensor_msgs/msg/CameraInfo` | Calibration. Without a calibration file it contains only the image width and height |
| `/image_raw/compressed` | `sensor_msgs/msg/CompressedImage` | JPEG-compressed copy of the image |
| `/image_raw/compressedDepth`, `/image_raw/theora`, `/image_raw/zstd` | | Other compressed formats, from the image transport plugins in the course image; you can ignore them |

The driver publishes one `/camera_info` message with each image, so `ros2 topic hz /camera_info` can be used to estimate the camera's frame rate. The test camera ran close to 30 at 640 x 480. Press `Ctrl+C` to stop the measurement. Use this topic for the rate check; `ros2 topic hz /image_raw` can underestimate the rate when it cannot keep up with full-size images. In testing it reported 3 to 12 messages per second for a camera publishing 30.

To stop the driver, press `Ctrl+C` in its terminal.

## 6. View the image

**rqt_image_view.** In the second terminal, run:

```bash
ros2 run rqt_image_view rqt_image_view
```

Choose `/image_raw` from the drop-down list at the top left of the window. If the list is empty, click the refresh button next to it.

**RViz.** Run `rviz2`. Click **Add** below the **Displays** panel, open the **By topic** tab, and choose **Image** under `/image_raw`. The image appears in a new **Image** panel below the **Displays** panel. RViz still shows a warning, `Fixed Frame: No tf data`, because nothing publishes coordinate frames; the Image display works without them. The same list also offers **Camera** under `/image_raw`; that display needs a calibrated camera, and without one it shows `CameraInfo/P resulted in an invalid position calculation (nans or infs)`.

## 7. Record a bag and play it on your VM

**Record on the lab computer.** In a container terminal, run:

```bash
cd ~/workspaces
ros2 bag record -o webcam_test /image_raw /camera_info
```

Press `Ctrl+C` to stop recording. The bag is the folder `~/workspaces/webcam_test`, which is also on the host because of the `-v ~/workspaces:/root/workspaces` mount. Check what it contains with:

```bash
ros2 bag info webcam_test
```

At 640 x 480 and 30 frames per second, `/image_raw` records about 28 MB per second, or about 1.6 GB per minute. To reduce storage use for longer recordings, record the compressed topic, which stores JPEG images:

```bash
ros2 bag record -o webcam_test /image_raw/compressed /camera_info
```

In testing, the compressed recording took about 2 MB per second, or about 120 MB per minute; the size depends on what the camera sees.

**Copy the bag to your VM.** In a host terminal on the lab computer (not in the container), run the following, with your NetID and your VM's host name:

```bash
scp -r ~/workspaces/webcam_test NETID@YOUR-VM.vm.duke.edu:~/workspaces/
```

In testing, the container created the bag folder and its files as `root`, with permissions that let other users read them, so `scp` should be able to copy them. If you get a permission error when deleting or renaming them on the host, use `sudo`, or change their owner first with `sudo chown -R $USER:$USER ~/workspaces/webcam_test`.

**Play it on your VM.** Start the course container on your VM as usual, then run:

```bash
ros2 bag play ~/workspaces/webcam_test
```

Add `--loop` to repeat the recording until you press `Ctrl+C`. While it plays, `ros2 topic list` shows the recorded topics, and you can view them with `rqt_image_view` or RViz as in Section 6.

If you recorded `/image_raw/compressed`, `rqt_image_view` can show it directly (choose `/image_raw/compressed` in the list). Nodes that subscribe to `/image_raw`, such as the Lab 9 hazard monitor, need the images decompressed. Run this in its own terminal while the bag plays:

```bash
ros2 run image_transport republish --ros-args -p in_transport:=compressed -p out_transport:=raw -r in/compressed:=/image_raw/compressed -r out:=/image_raw
```

It publishes the decompressed images on `/image_raw` as `rgb8`.

## 8. Use the camera with the Lab 9 hazard monitor

The Lab 9 starter repository's `README.md` has a section, "Optional: using your sensor code in your project", on running `hazard_monitor` with a real camera. Use the `turtlebot4-jazzy-latest` image for this, since the monitor uses TurtleBot 4 message packages that `base-jazzy-latest` does not include.

Run the camera driver and the monitor in the same container. In testing, a monitor in one container received no images from a driver in another container on the same computer. Start the container with your Lab 9 repository mounted (the path below is an example; use yours) and with the camera:

```bash
xhost +local:docker
docker run --rm -it \
  --name webcam \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v ~/workspaces:/root/workspaces \
  --device /dev/video0 \
  ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:turtlebot4-jazzy-latest \
  bash -c 'echo "export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST" >> ~/.bashrc && exec bash'
```

The last line is needed because this image's `.bashrc` sets discovery to `SUBNET`, which would override an `-e ROS_AUTOMATIC_DISCOVERY_RANGE` option. Install and start the driver as in Sections 4 and 5. Then, in a second terminal in the same container (`docker exec -it webcam bash`), build the Lab 9 workspace as in the lab and, from the root of your Lab 9 repository, run the command from that README:

```bash
ros2 run lab09_sensors hazard_monitor --ros-args -p image_topic:=/image_raw
```

Set `use: true` in `thresholds.yaml` only for the sensors you have. With only a webcam, that is `camera`. The monitor prints `Sensors in use: camera.` when it starts. Until you have written `marker_seen` in `sensing.py`, it prints `sensing.marker_seen is not written yet; skipping the camera.` Once you have, it prints `camera: hazard` and publishes `camera` on `/hazard_stop` while your function returns `True`.

The same command works with a bag from Section 7 playing in that container (for a compressed bag, with the `republish` command running too).

## Running on Windows with WSL2 and usbipd-win

!!! warning "Tested on one laptop"
    This section was tested on one staff Windows 11 laptop with one webcam. Results on other computers and cameras may differ.

On Windows, Docker Desktop runs Linux containers inside WSL2, and WSL2 cannot see USB devices until you attach them with [usbipd-win](https://github.com/dorssel/usbipd-win). Windows cannot use the camera while it is attached to WSL2. Windows plays its device connect and disconnect sounds each time you attach and detach the camera.

On the test laptop, the camera's `YUYV` images arrived through WSL2 incomplete: each 640 x 480 image had only its top 24 rows, and the rest was solid green. `v4l2_camera` cannot read the camera's `MJPG` stream, so on that laptop it could not produce complete images. The `usb_cam` driver reading the camera's `MJPG` stream produced complete images at 30 frames per second. The steps below use `usb_cam`.

1. Install usbipd-win. In PowerShell, run `winget install --interactive --exact dorssel.usbipd-win`, or download the `.msi` installer from the project's releases page.
2. Start Docker Desktop. `usbipd` attaches the camera through Docker Desktop's WSL distribution, so you do not need to open another WSL terminal.
3. Plug in the webcam. In PowerShell, list the USB devices and note the BUSID of the webcam (for example, `3-1`). The webcam may appear under a generic name such as `USB 2.0 Camera`; it is the entry that appears when you plug it in.

    ```powershell
    usbipd list
    ```

4. Share the webcam. This needs PowerShell opened **as administrator**, once per device:

    ```powershell
    usbipd bind --busid 3-1
    ```

    If `usbipd` prints `warning: Unknown USB filter '...' may be incompatible with this software; 'bind --force' may be required.`, another program on your computer filters USB devices. On the test laptop the filter was `CsDeviceControl`, from the CrowdStrike security software that Duke installs on the computers it manages. With the plain `bind`, the camera stopped sending images after about 18 frames. `usbipd bind --force --busid 3-1` fixed the `MJPG` stream. If the computer is managed by Duke or another organization, ask its IT staff before using `--force`, since it works around their software.

5. Attach the webcam to WSL. An ordinary PowerShell window is enough. Repeat this step each time you plug the camera in or restart the computer:

    ```powershell
    usbipd attach --wsl --busid 3-1
    ```

    `usbipd list` should then show the webcam as `Attached`.

6. Start the container from PowerShell. Docker Desktop's WSL2 system provides the display, so `xhost` is not needed, and the X11 socket is at a different path than on Linux:

    ```powershell
    docker run --rm -it `
      --name webcam `
      --net=host `
      -e DISPLAY=:0 `
      -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST `
      -v /run/desktop/mnt/host/wslg/.X11-unix:/tmp/.X11-unix:ro `
      -v "${HOME}/workspaces:/root/workspaces" `
      --device /dev/video0 `
      ghcr.io/mems-intro-to-robotics/mems-robotics-toolkit:base-jazzy-latest
    ```

    The backtick at the end of each line continues the command in PowerShell. `${HOME}/workspaces` is the `workspaces` folder in your Windows user folder. For Section 8, replace the image with `turtlebot4-jazzy-latest` and add the `bash -c ...` line from that section.

7. Check the camera with the commands in Section 3. The webcam's first entry, `/dev/video0`, should list its formats. If the container has no `/dev/video0`, or `docker run` fails with `error gathering device information`, one possible cause is that the WSL2 kernel has not loaded its USB video driver (`uvcvideo`). On the test laptop it loaded on its own when the camera was attached with WSL kernel 6.18.33 (2026-11-03), but not with kernel 6.18.58 (2026-11-12, with a RealSense camera). If it has not loaded, load it in PowerShell, then start the container again:

    ```powershell
    docker run --rm --privileged -v /lib/modules:/lib/modules alpine sh -c "apk add -q kmod && modprobe uvcvideo"
    ```

    You may need to load the driver again after Windows or Docker Desktop restarts.
8. Install and run `usb_cam`:

    ```bash
    apt-get update && apt-get install -y ros-jazzy-usb-cam
    ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video0 -p pixel_format:=mjpeg2rgb -p image_width:=640 -p image_height:=480
    ```

    `usb_cam` publishes the same topics as `v4l2_camera` (`/image_raw`, `/camera_info`, and the compressed topics), with `rgb8` images, so Sections 5 to 8 apply from the topic check onward. Its `frame_id` is `default_cam`. At startup on the test laptop, it printed `Cannot open device: /dev/video1, double-check read / write permissions for device` (the container has only `/dev/video0`), messages such as `unknown control 'exposure_auto'`, and the calibration file messages from Section 5. It continued publishing images despite these messages.

When you are done, run `usbipd detach --busid 3-1` in PowerShell or unplug the camera. Windows can use the camera again after that. On the test laptop, detaching and attaching the camera while the container was running restored it as `/dev/video0`; restarting the driver was enough to resume streaming without restarting the container.

## Common problems

**`Package 'v4l2_camera' not found`.** The driver is not installed in this container. Run the install in Section 4.

**`error gathering device information while adding custom device "/dev/video0"`.** `docker run` cannot find the camera. Check that it is plugged in and that `ls /dev/video*` on the host lists it. On Windows, check that `usbipd list` shows it as `Attached`.

**`Failed opening device /dev/video0: No such file or directory (2)`.** The container cannot see the camera. Check that you started it with `--device /dev/video0` and that `ls /dev/video*` on the host still lists the device. After this error the driver keeps running but publishes nothing; stop it with `Ctrl+C`.

**`Current pixel format is not supported yet: MJPG`.** The driver was asked for Motion-JPEG, which it cannot read. It then prints `terminate called after throwing an instance of 'cv_bridge::Exception'` and stops with `[ros2run]: Aborted`. Use `-p pixel_format:=YUYV` (the default) and an `image_size` that Section 3 lists for `YUYV`. If the camera only offers `MJPG`, or you need a large image at full frame rate, use the `usb_cam` driver with `-p pixel_format:=mjpeg2rgb` as in step 8 of [Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win); see its documentation in the References.

**The image size is not what you asked for.** The camera may not offer that size in the pixel format you requested. Pick a size from the list in Section 3.

**The frame rate is low.** Measure it with `ros2 topic hz /camera_info`, not `/image_raw` (Section 5). Large `YUYV` sizes can limit the frame rate. Use 640 x 480, or `usb_cam` with `MJPG` for large sizes. A dim scene can also lower the frame rate when the camera lengthens its exposure.

**The image is solid gray.** Check that nothing covers the lens. Some webcams have a sliding privacy shutter.

**On Windows, most of each image is solid green, or the driver stops after a few frames with `Select timeout, exiting...`.** These symptoms occurred during testing through `usbipd`; they do not identify the cause on every computer. Try `usb_cam` with `MJPG` (step 8 of [Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win)), and read the note on USB filter warnings in step 4. If that does not help, use a lab computer.

**`rqt_image_view` shows nothing.** Check that `ros2 topic hz /camera_info` reports messages. If it does, choose the topic again in the drop-down list. If it does not, check the driver's terminal for errors.

**No window opens (`could not connect to display`).** On a lab computer, run `xhost +local:docker` on the host and start the container again with the `DISPLAY` and `/tmp/.X11-unix` options from Section 2. On Windows, use the options in step 6 of [Running on Windows](#running-on-windows-with-wsl2-and-usbipd-win).

**The hazard monitor gets no images.** Run the driver and the monitor in the same container (Section 8).

**Your VM does not see the camera's topics.** With the container configured as shown here, ROS discovery is limited to the lab computer by `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`, so the VM cannot discover the camera's topics. Record a bag and play it on the VM (Section 7).

??? note "To verify on hardware (staff checklist; remove when done)"
    Checked without a camera on 2026-11-03: `v4l2_camera` 0.7.3 installs with `apt-get` in the published `turtlebot4-jazzy-latest` image, which does not include it by default; parameter names and defaults (source and binary); topic list and `/image_raw` QoS (node started with no device); the `Package 'v4l2_camera' not found` and `Failed opening device` messages; `v4l2-ctl` and `lsusb` present in the image; the `republish` command subscribes to `/image_raw/compressed` and publishes `/image_raw`.

    Checked with a webcam on 2026-11-03: Amazon Basics webcam, USB `208e:2cc9` (manufacturer string `LX-260325-A`), on the staff Windows 11 laptop: WSL 2.7.14, kernel 6.18.33.2, `usbipd-win` 5.3.0, Docker Desktop 29.9.2 (driven from PowerShell), CrowdStrike Falcon running. Confirmed:

    - [x] Two entries, `/dev/video0` (formats listed) and `/dev/video1` (no formats).
    - [x] `v4l2-ctl --list-devices` and `--list-formats-ext` work in the container with only `--device /dev/video0`.
    - [x] `-p image_size:="[640,480]"` is accepted as written (`Requesting format: 640x480 YUYV`, `ros2 param get` gives `[640, 480]`).
    - [x] Startup log shows formats and controls; `possibly slow conversion` appears once. This camera also logs `[ERROR] Failed getting value for control 10092545: Permission denied (13)` and the calibration-file `[ERROR]`.
    - [x] `ros2 topic hz /camera_info` reports 29.6 to 29.8 Hz (both drivers); `ros2 topic hz /image_raw` reported 3.0 to 11.8 Hz at the same time. Use `/camera_info` for the rate check.
    - [x] `pixel_format:=MJPG` in `v4l2_camera`: `Current pixel format is not supported yet: MJPG 1196444237`, then `cv_bridge::Exception ... Unrecognized image encoding []` and `[ros2run]: Aborted`.
    - [x] `usb_cam` with `pixel_format:=mjpeg2rgb`: 30 Hz, 240 of 240 frames complete in an 8 s bag, `frame_id` `default_cam`.
    - [x] Raw 640 x 480 bag: 211.1 MiB for 240 frames over 8.04 s (about 27.5 MB/s). Compressed: 18.3 MiB over 9.65 s, 288 frames.
    - [x] Bag folder and files created as `root`, mode 755/644 (seen in the container). These permissions allow `scp` to read the files without `chown`. Copying from a Linux host has not been tested.
    - [x] Raw bag playback (`/camera_info` 29.7 Hz); compressed bag playback, the `republish` command, and `hazard_monitor` on the result (`camera: hazard`), all in one `turtlebot4-jazzy-latest` container on the laptop, not on a VM.
    - [x] `hazard_monitor` on a live webcam (`usb_cam`) in `turtlebot4-jazzy-latest`: stub prints `not written yet; skipping the camera`; with `marker_seen` written it publishes `camera` on `/hazard_stop`. A monitor in a second container (`--net=host`, no `--ipc=host`) received nothing, not even `/camera_info`.
    - [x] `docker run --device /dev/video0` with the camera detached fails with `error gathering device information ...`. Detach and attach while the container runs: the device came back as 81:0 and `usb_cam` ran again at 29.8 Hz without restarting the container.
    - [x] WSL2: `usbipd list` and `usbipd attach` work without administrator rights; `bind` needs it. `attach` used the `docker-desktop` distribution, no Ubuntu terminal needed. `uvcvideo` loaded automatically on attach (kernel 6.18.33; on 2026-11-12 with kernel 6.18.58 it did not, for a RealSense, and `modprobe` from a privileged container fixed it; the webcam was not retested on that kernel). Docker Desktop started from PowerShell passes `/dev/video0` with `--device`. WSLg socket at `/run/desktop/mnt/host/wslg/.X11-unix` mounts and RViz starts (`OpenGl version: 4.5`).
    - [x] WSL2 streaming: with the plain `bind` (CrowdStrike `CsDeviceControl` warning), YUYV gave 0 frames from `v4l2-ctl` and MJPG about 18 frames, then stopped; the kernel log showed `usb usb1: Not yet implemented` (from `vhci_get_frame_number`) and `vhci_hcd: urb->status -104`. With `bind --force`, MJPG ran 300 frames at 29.7 fps, but every YUYV frame from `v4l2_camera` had only 24 of 480 rows (286 of 286 frames). The same camera captures 30 fps YUYV 640 x 480 in Windows with ffmpeg.

    Still to confirm:

    - [ ] The whole guide on a lab computer with native USB, especially `v4l2_camera` with `YUYV` (not possible over WSL2 with this camera).
    - [x] `rqt_image_view` on WSLg: `/image_raw` chosen from the drop-down shows live video (`usb_cam`). RViz with Fixed Frame `default_cam`: the **Camera** display under `/image_raw` receives messages but reports `CameraInfo/P resulted in an invalid position calculation (nans or infs)` (uncalibrated `camera_info`); note added to Section 6. The Global Status still shows `Fixed Frame: No tf data`.
    - [x] RViz **Image** display under `/image_raw` shows live video in a panel below Displays, with the `No tf data` warning still present. The Fixed Frame step was removed from Section 6 because it does not clear the warning and the Image display does not need it.
    - [ ] `lsusb` and `ls /dev/video*` on a lab computer host; `xhost` and the Section 2 command on a lab computer.
    - [ ] `scp` from a lab computer to a VM with NetID login; playback and `rqt_image_view` on `/image_raw/compressed` on a VM.
    - [ ] Physical unplug and replug on a lab computer while the container runs.
    - [ ] Whether a student laptop without CrowdStrike streams `YUYV` over WSL2, and whether a WSL2 distribution with Docker Desktop's integration behaves like PowerShell (the test laptop's Ubuntu distribution runs its own Docker Engine, so it was not tested).
    - [ ] Raspberry Pi 5: the ARM64 image name and whether it needs the same install step (the `base-pi5` Dockerfile does not list `ros-jazzy-v4l2-camera`).

## References

- `v4l2_camera` documentation (ROS 2 Jazzy branch): [gitlab.com/boldhearts/ros2_v4l2_camera](https://gitlab.com/boldhearts/ros2_v4l2_camera/-/tree/jazzy)
- `usb_cam` driver: [github.com/ros-drivers/usb_cam](https://github.com/ros-drivers/usb_cam)
- `image_transport` and `republish`: [github.com/ros-perception/image_common](https://github.com/ros-perception/image_common/tree/jazzy)
- `rqt_image_view`: [github.com/ros-visualization/rqt_image_view](https://github.com/ros-visualization/rqt_image_view)
- Recording and playing back data (ROS 2 Jazzy tutorial): [docs.ros.org](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html)
- `docker run --device`: [docs.docker.com](https://docs.docker.com/reference/cli/docker/container/run/#device)
- Connecting USB devices to WSL: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/wsl/connect-usb) and [github.com/dorssel/usbipd-win](https://github.com/dorssel/usbipd-win)
