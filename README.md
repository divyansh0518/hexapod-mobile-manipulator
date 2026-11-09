# Hexapod Mobile Manipulator

**A six-legged robot with an arm, built for places where wheels don't work and people shouldn't go.**

18 leg servos · arm with gripper · remote control with live video · onboard sensing

<!-- HERO: best photo of the finished robot, or a GIF of it walking -->
![Hexapod mobile manipulator](media/final/robot_01.jpg)

[Hardware](docs/hardware.md) · [Power system](docs/power.md) · [Controls](docs/controls.md) · [Performance](docs/performance.md) · [Credits](NOTICE.md)

---

## Why I built it

Mines, nuclear power plants, pipe-filled industrial spaces, collapsed buildings in a rescue
mission: they have the same problem for a robot. The floor is cluttered with pipes, cables, rubble and steps, and a wheeled robot gets
stopped by the first obstacle. Legs can step over things, and an arm lets the robot do
something once it gets there: move debris, press, pick up and carry a light object.

<!-- Add: link to demo video -->
**Demo video:** 

## Design Inspiration

The robot is designed around one central idea: combine animal-inspired locomotion, stability on difficult terrain, and manipulation capabilities in a single platform.

**Crab-inspired morphology:**  The wide, laterally distributed leg arrangement takes inspiration from crabs and provides a broad support base. This geometry is useful for navigating cluttered terrain where wheel-based mobility can become restrictive. The current platform uses forward walking, while sideways crab locomotion remains a future extension.

**Insect-inspired locomotion:**  The robot uses an alternating tripod gait, inspired by the walking patterns of insects such as ants and cockroaches. Legs 0, 2 and 4 alternate with legs 1, 3 and 5, creating alternating three-leg support phases for coordinated movement.

**Integrated manipulation:**  Unlike a conventional hexapod, this platform carries a robotic arm and gripper on its upper body. The legs handle terrain traversal while the arm enables object interaction. The arm folds over the chassis during locomotion to maintain a compact configuration.
### References 

1. **Chen, Y. et al. (2022).** [Sideways crab-walking is faster and more efficient than forward walking for a hexapod robot.](https://doi.org/10.1088/1748-3190/ac6847) *Bioinspiration & Biomimetics, 17(4).*

2. **Full, R. J. & Tu, M. S. (1990).** [Mechanics of six-legged runners.](https://doi.org/10.1242/jeb.148.1.129) *Journal of Experimental Biology, 148, 129–146.*

3. **Ting, L. H., Blickhan, R. & Full, R. J. (1994).** [Dynamic and static stability in hexapedal runners.](https://doi.org/10.1242/jeb.197.1.251) *Journal of Experimental Biology, 197, 251–269.*

4. **Mahapatra, A., Roy, S. S. & Pratihar, D. K. (2019).** [Study on feet forces' distributions, energy consumption and dynamic stability measure of hexapod robot during crab walking.](https://doi.org/10.1016/j.apm.2018.09.015) *Applied Mathematical Modelling, 65, 717–744.*

5. **Zheng, Y. et al. (2022).** [Different manipulation mode analysis of a radial symmetrical hexapod robot with leg–arm integration.](https://doi.org/10.1007/s11465-021-0664-0) *Frontiers of Mechanical Engineering, 17, Article 8.*
## Specifications

| | |
|---|---|
| Legs | 6 legs x 3 joints (coxa, femur, tibia), 18 x DS3235 Pro 35 kg.cm coreless metal-gear digital servos, 180 deg, 7.4 V |
| Arm | base, shoulder (2 servos), elbow, 2 wrist joints, gripper. 4 x MG996R (base, shoulder, elbow) and 3 x MG90 (wrists, gripper) |
| Main controller | Arduino Mega 2560 |
| Remote | Arduino Uno, 2 joysticks, 2 pots, toggles, 16x2 LCD, nRF24L01 |
| Camera | ESP32-CAM, MJPEG over its own WiFi network |
| Edge payload | UNIHIKER K10: camera, screen, temperature, humidity, light, accelerometer |
| Body tilt | K10 accelerometer (3-axis), used for tilt warning. |
| Power | 3S LiPo, 5200 mAh (11.1 V nominal, 12.6 V full). Three regulated rails: legs 7.4 V, arm 6.0 V, logic 5 V. See [docs/power.md] |
| Firmware | Arduino C++ (PlatformIO), MicroPython on the K10 |

## Build

<!-- Replace each image and write a caption in your own words. Add rows if you like. -->

| | | |
|---|---|---|
| ![](media/printing/printing_01.jpg) | ![](media/assembly/assembly_01.jpg) | ![](media/assembly/assembly_02.jpg) |
| _Printing_ | _Leg assembly_ | _Body_ |
| ![](media/electronics/wiring_01.jpg) | ![](media/electronics/power_01.jpg) | ![](media/arm/arm_01.jpg) |
| _Wiring_ | _Power system_ | _Arm mounted on the body_ |
| ![](media/final/robot_02.jpg) | ![](media/final/testing_01.jpg) | ![](media/final/robot_03.jpg) |
| _Finished robot_ | _Testing_ | _Close-up_ |

## How it works

```mermaid
flowchart LR
    R["Remote (Uno + LCD)"] -->|"nRF24, 50 Hz"| M["Arduino Mega 2560"]
    M --> L["18 leg servos"]
    M --> A["Arm: 7 servos"]
    C["ESP32-CAM"] -. "WiFi AP" .-> V["Phone or laptop"]
    K["UNIHIKER K10"] --> S["Screen, sensors, tilt alert"]
```

**Control.** The remote sends a packet 50 times a second. Toggle 1 picks the mode. In walk
mode the joysticks drive the gait and the arm holds its pose. In arm mode the joysticks move
arm joints, the pots set the wrist and gripper, and the legs stand. If no packet arrives for
half a second, the robot stands still and the arm holds.

**Gait.** Tripod gait. Each foot target goes through inverse kinematics on the Mega to get
the coxa, femur and tibia angles.

**Power.** The battery never touches a servo or a board directly. The 3S pack feeds a 7.4 V leg rail
(two converters, left and right), a 6.0 V arm rail (the highest voltage both MG90 and MG996R
accept) and a 5 V logic rail, all behind a fuse and a master switch. Details and sizing in [docs/power.md](docs/power.md).

**2.4 GHz.** The control link and the camera share the band, so the nRF24 runs on channel
76 and the camera's WiFi is pinned to channel 1. They don't overlap.

## Limitations

- Walking is open loop. The K10's accelerometer is used for tilt warning only. With no gyroscope
  there is no sensor fusion and no body leveling yet.
- Video goes over WiFi and has much shorter range than the control link.
- Radiation, dust and water are not addressed. Real nuclear or mine work would need a
  hardened, sealed machine.


Built by Divyansh Rahangdale.

