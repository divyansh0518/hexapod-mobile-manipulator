# Reproducible experiment plan

Keep the software revision/archive hash, config, battery state, hardware masses,
servo model, surface and camera mounting with every dataset. Record failed
trials as well as successes. Use `experiments/field_trials.csv` as the starting
schema. The table is empty intentionally; simulation output is not field data.

## Gait comparison

On a level track, compare equal stride/period settings for tripod, paired ripple
and wave. Randomize gait order; repeat each condition at least five times. Record
travel distance/time, successful completion, body tilt from a separately fitted
IMU, foot slips and energy from voltage/current logging. Report mean and spread,
not only the fastest run. Repeat with safe foam obstacles only after level
walking works. Open-loop trajectories alone do not establish terrain adaptation.

Vary stride, lift and period one at a time. Compare ideal support margin from the
kinematic CSV with contact observations. Actual centre of mass should be measured
with arm stowed and extended; do not equate body origin with combined COM.
A useful future extension is contact/IMU feedback to modify foot placement.

## Manipulation

Fix the base in a supported stance, calibrate the arm and survey a grid of
reachable target markers. Command a passive probe approach with no contact.
Measure 3D position error and repeatability independently (ruler jig, tracking
camera or motion capture), not by reading FK back from the same requested joint
angles. Test several reach directions and loads. Record missed targets and IK
rejections. A grip-success experiment needs an actual active gripper and a
revised actuator/DOF count.

Compare full-pose IK and position-only IK in simulation, then validate orientation
with a marked tool frame. Measure support/COM changes as the arm extends before
attempting any mobile manipulation with payload.

## Radio range and packet delivery

The **1000–1200 m distance is a target to test**, not an established capability.
Record radio variant, antenna gains/orientation, PA setting, RF channel, supply,
height above ground, line of sight and interference conditions. Use transmitter
`sent` / `acked` counter deltas for per-interval acknowledged delivery ratio:
`delta_acked / delta_sent`. Log receiver sequence progression where possible.
An ACK is link evidence, not proof a host control action occurred. Report
watchdog events and longest command gaps. Stationary supported hardware should
be used for the distance test before remote walking.

Do not infer command latency from packet delivery. Measure a transmitter input
and corresponding receiver/servo event with a common clock or logic analyser;
report median, p95 and maximum. Software command frequency is nominally 50 Hz;
it is not a measured end-to-end latency.

## FPV latency

Use an independent FPV camera/VTX/receiver. Preview a USB capture receiver:

```bash
python tools/fpv_monitor.py --source 0
python tools/fpv_monitor.py --source 0 --record media/demo.mp4
```

A supported RTSP URL can be used as `--source`, but buffering depends on the
camera, backend and network. A buffer-size request is best effort. Film an LED
and the receiver display together using a high-speed reference camera; count
frames between physical change and displayed change. Report frame rate, capture
backend, video resolution and p50/p95 latency. Do not describe this as
low-latency FPV until measured. NRF24 carries commands, never the video stream.

## Vision

For the K10, report exact firmware/mode, lighting, update rate and identification
accuracy on a labelled test set. For an external detector, report model source,
license, classes, held-out images, precision/recall, frame rate and compute host.
Measure projection error independently over the actual workspace. Include
occlusion and false-positive cases. Target selection should fail closed when
calibration or geometry is invalid.

## Failure tests

On a stand: disconnect host USB, release deadman, power off transmitter, block or
unplug range sensor, open NC stop loop and inject a bad-CRC frame. Verify and
film signal inhibition and observe mechanical effects. Do not test power loss
with an unsupported loaded robot. Record recovery procedure and behaviour.
