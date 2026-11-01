# Kinematics and control design

## Leg model

For leg i, mount `m=(mx,my,0)` and yaw `psi=atan2(my,mx)`. Mathematical joint
angles are q0 (coxa yaw), q1 (femur pitch), q2 (knee, negative flexion branch).
With a,b,c the coxa/femur/tibia lengths:

```text
r = a + b cos(q1) + c cos(q1 + q2)
x = mx + r cos(psi + q0)
y = my + r sin(psi + q0)
z = b sin(q1) + c sin(q1 + q2)
```

Inverse kinematics solves the planar two-link chain after subtracting a from
horizontal radius. Targets outside the annulus are rejected, rather than
silently changing the requested position. Servo conversion is independent:
`servo_deg = offset_deg + sign * degrees(q)`. A knee with negative mathematical
angle can therefore map to a positive servo angle using sign -1.

## Gait scheduling

Phases are defined by **swing start**, and stance occupies the remainder of a
cycle. Offsets in leg order RF,RM,RR,LR,LM,LF:

| Gait | Stance duty | Swing offsets | Ideal swing legs |
|---|---|---|---|
| Tripod | 1/2 | 0,1/2,0,1/2,0,1/2 | 3 |
| Ripple (paired variant) | 2/3 | 0,1/3,2/3,0,1/3,2/3 | 2 |
| Wave | 5/6 | 0,1/6,2/6,3/6,4/6,5/6 | 1 |

Ripple terminology varies; this repository specifies the paired sequence
explicitly. During stance, feet sweep backward relative to the body. During
swing, smoothstep horizontal interpolation and a squared-sine lift return the
foot forward. Rotation acts about the body origin. Lateral translation is also
supported. Control commands are normalized, not a calibrated metres-per-second
velocity. Period is 2 s by default and runs from a monotonic host clock.

A support-polygon metric reports signed distance of an assumed body-centred
COM projection to the ideal convex contact polygon. It is positive inside and
negative outside. It is a **geometric diagnostic**, not proof of stability.
Arm extension, inertia, slipping, compliance and ground contact are not sensed.
Gait changes and stopping use servo slew limits but do not coordinate touchdown
transitions. Change gaits only at rest during hardware experiments.

## Manipulator

Six revolute axes use a local-axis rotation followed by local-link translation.
Forward kinematics multiplies homogeneous transforms. Inverse kinematics uses
finite-difference Jacobians and damped least squares, joint-limit clipping and
bounded iteration steps. It accepts a position or a full rotation-matrix target.
The orientation residual is the SO(3) rotation logarithm, scaled by a 70 mm
characteristic length to balance position and angular error.

Default tolerance: 0.5 mm position and 0.02 rad orientation (when requested).
These are numerical convergence tolerances, not real arm accuracy. Singular or
unreachable goals are rejected. No obstacle collision model, force controller,
learned policy, gravity compensation or grasp planner is implemented.

The live controller only accepts targets after the base has settled at its
neutral command pose. A new walking command during arm motion terminates the
host run with a stop frame. Arm planning is position-only in the live QR path;
the separate pose IK API supports orientation targets for experiments.

## Wire protocol

Host → Mega, every 20 ms, exactly 56 bytes, all integers little-endian:

| Bytes | Field |
|---|---|
| 0–1 | ASCII HX |
| 2 | Version = 1 |
| 3 | Flags: bit 0 arm, bit 1 latch stop; other bits rejected |
| 4–5 | uint16 sequence, wrapping |
| 6–53 | 24 uint16 servo commands, 0.1 degree units |
| 54–55 | CRC-16/CCITT-FALSE of bytes 0–53, init 0xFFFF, polynomial 0x1021 |

Frames are range-checked as a unit. Serial partial-frame timeout is 30 ms.
Noise loses at most a subsequent frame before a fresh HX header is found.
Sequence is diagnostic, not replay protection; the link is trusted local USB.
The receiver initializes servo signals only after all enable conditions pass.
Its 20 ms output step is bounded to 1.2 degrees (60 degrees/s).

NRF packet, 16 bytes: magic 0xA5 (u8), version 1 (u8), sequence (u16), X/Y/yaw
(three i16, -1000…1000), gait (u8, 0 tripod/1 ripple/2 wave), deadman flags (u8,
bit 0), transmitter uptime (u32). Both ends use channel 90, 250 kbps, fixed 16-byte
payload, hardware CRC16 and acknowledgements. Channel/power must be selected for
your deployment. Default low PA is for bench tests, not a 1 km range claim.

Mega → host is 10 Hz JSON status with range, axes, radio freshness, deadman,
local switches and whether output is enabled. Host and radio timeouts are 250 ms.
No embedded controller autonomously keeps walking when the Python host is lost.

## Inhibition and recovery

Range below 250 mm or timeout, missing command source, released deadman/enable,
host expiry, uncalibrated firmware or a latched stop inhibits output. The Mega
detaches servo signals, so gravity can still move joints. Opening the NC loop
latches stop. After it is restored, an explicit disarm frame clears the latch;
then new valid armed frames and all physical enable conditions are required.
Software shutdown transmits a stop frame; unplugging the host triggers watchdog.
The controller's numerical hold behaviour does not override firmware detachment.
