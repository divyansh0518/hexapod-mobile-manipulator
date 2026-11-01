# Vision and target-directed manipulation

## Supported paths

1. **K10 native QR identification:** `edge/k10/main.py` runs the vendor native
   scanner and emits JSON over USB. Host resolves a QR string against a table
   of surveyed body-frame target positions, solves arm IK and approaches that
   location while the base remains stopped. This is discrete visual
   identification plus a known-position lookup, not image-based pose estimation.
2. **K10 native cat/dog demonstration:** set `MODE="catdog"`. Native classification
   events are displayed/emitted but deliberately never become arm targets.
3. **Optional host ONNX detection:** an external post-NMS model detects labelled
   objects. A calibrated pixel ray intersects a known plane in the body frame.
   The projection and IK functions are implemented; a compatible trained model,
   class labels and real camera calibration must be supplied separately.

There is no supplied custom object detector for the K10, no training dataset,
no measured FPS and no model weights. Generic real-time object detection and
classification on K10 must not be claimed from the QR/classification demos.

## K10 setup

Use the official [MicroPython setup guide](https://www.unihiker.com/wiki/K10/GettingStarted/gettingstarted_mpy/)
and the [native AI API examples](https://www.unihiker.com/wiki/K10/Examples/examples_mpy/).
Install matching vendor firmware, copy the script to the board as `main.py`, and
run it. Close Thonny/serial monitor before opening the port from the host. Runtime
API compatibility still needs testing on your K10. Vendor documentation for
firmware 0.9.8 says native AI and WiFi cannot run simultaneously; this design
uses USB events and an independent FPV link.

Print a QR code containing `DEMO_TARGET`. The default table coordinate is only a
simulation example. Replace it with a measured target in the current body frame.
Moving the robot invalidates a world-fixed target lookup unless you re-survey or
transform the coordinate. Validate a tool approach above the target; use passive
markers/blocks for manipulation experiments. Never use the animal classifier
to direct physical interaction with animals.

Example event: `{"kind":"qr","code":"DEMO_TARGET"}`.

## Host model contract

```bash
hexapod vision-host --model models/detector.onnx --labels models/labels.txt --camera 0
```

Model files are user-supplied paths, not included artifacts. Input must be fixed
`[1,3,H,W]` float32 RGB in [0,1]. The exporter must match direct image resize
without letterboxing, and output `[1,N,6]` rows `[x1,y1,x2,y2,score,class_id]` after
NMS, in input-pixel coordinates. Raw YOLO tensor formats are rejected; export a
compatible postprocessing graph or adapt the decoder to your model's real spec.
Output is JSON lines, suitable for analysis or a serial event producer. The live
CLI consumes a serial JSON stream via `--vision-port`; host ONNX stdout is not
a direct built-in transport to `run`. To integrate a host camera application,
call `OnnxDetector.detect`, `resolve_target` and `Controller.set_target` in the
same application after applying the same live-enable and stationary checks.

## Camera calibration and projection

`camera.K` is the intrinsic matrix. `T_body_camera` maps camera coordinates
(right, down, optical-forward) to body coordinates. Both example matrices are
synthetic and `calibrated=false` blocks pixel-based action. Measure intrinsics
and lens distortion, undistort pixels before projection, estimate extrinsics
with a calibration board, and measure the known plane's body Z coordinate.
Then set the calibration flag true. Current projection assumes a fixed body
and fixed camera, ignores distortion and cannot estimate unknown object height.
A top-down demo plane may be useful off-robot; the example camera placement is
not a verified onboard mounting design.

For pixel p, body ray is `R K^-1 [u,v,1]`. Intersection with Z=z_plane uses
`s=(z_plane-origin_z)/ray_z`. Parallel rays and intersections behind the camera
are rejected. A point on a pixel-centre ray is only appropriate for contact on a
known plane; it does not establish a grasp pose. Test projection against known
landmarks across the image before motion, and add tool clearance above the
plane. Autonomous final contact and gripper actuation are not implemented.
