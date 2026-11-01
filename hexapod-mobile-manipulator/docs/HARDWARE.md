# Hardware, wiring and calibration

## Reference-backed geometry

All lengths are millimetres. Body axes: X forward, Y left, Z up. Leg order is
RF, RM, RR, LR, LM, LF, viewed from above.

| Quantity | Supplied sketch | Integrated default |
|---|---:|---:|
| Coxa length | 38.0 | 38.0 |
| Femur length | 86.25 | 86.25 |
| Tibia length | 160.5 | 160.5 |
| Step length | 60.0 | 40.0 |
| Step lift | 100.0 | 25.0 |
| Neutral foot Z | -40.0 | -100.0 |
| Foot radius outward from hip | FK-derived | 205.0 |

The new step/stance values are conservative **software design defaults**, not
measured improvements. The original 100 mm lift from a -40 mm foot height can
place the ideal foot above the hip plane. New defaults reduce that excursion.
Check clearance and linkage geometry on the real machine before enabling.

| Leg | Mount X,Y | Coxa/femur/tibia Mega signal pins |
|---|---|---|
| RF | 100.94, -57.11 | 28,29,30 |
| RM | 0, -105.72 | 25,26,27 |
| RR | -100.94, -57.11 | 22,23,24 |
| LR | -100.94, 57.11 | 31,32,33 |
| LM | 0, 105.72 | 34,35,36 |
| LF | 100.94, 57.11 | 37,38,39 |

## Proposed bill of materials

| Item | Count | Selection / role |
|---|---:|---|
| Arduino Mega 2560 | 1 | 24 Servo-library channels; USB host link |
| Arduino Uno | 1 | Handheld transmitter |
| High-torque metal-gear position servos | 24 | Torque, voltage, current and travel must match your mechanics |
| NRF24L01+ modules | 2 | Matching antenna systems; PA/LNA variants optional after supply review |
| UNIHIKER K10 | 1 | Native vendor MicroPython vision |
| Laptop or Linux companion | 1 | Python gait/arm computation; additional hardware for untethered operation |
| HC-SR04-compatible range sensor | 1 | Front distance interlock; 5 V logic at Mega |
| Three joystick/potentiometer axes | 3 | Forward, lateral, turn |
| Momentary deadman and selector switches | 3 | Uno D4, D5, D6 |
| Enable switch, NC stop loop, power cut-off | 1 each | Independent local controls |
| Regulated servo power, distribution and fuse | As sized | Separate from logic supply |
| Regulated 3.3 V radio supply + decoupling | 2 | Size to selected radio, especially PA/LNA |
| Independent FPV camera/VTX/receiver | 1 set | Separate radio/video system; permitted local channel/power |
| USB video capture adapter | Optional | Host preview or recording |

Do not choose a supply by summing nominal running current alone. Use the actual
servo datasheet and measure simultaneous current peaks. The required battery,
regulator rating, fuse and wiring gauge depend on that result. Servo torque
claims and payload cannot be derived from the provided sketch.

## Mega receiver wiring

| Function | Pins / connection |
|---|---|
| NRF CE / CSN | D2 / D3 |
| NRF MOSI / MISO / SCK | D51 / D50 / D52 |
| Mega hardware SS | D53 configured output; not a servo channel |
| NRF VCC | Dedicated regulated 3.3 V, common ground; never 5 V |
| Local NC stop loop | D4 to GND when healthy; opening loop latches stop |
| Local enable | D5 to GND while held/enabled |
| Front ultrasonic trigger / echo | D6 / D7; 5 V compatible sensor |
| Arm J0–J5 signals | D40,41,42,43,44,45 |
| Leg signals | Table above |
| Python host | USB serial, 115200 baud |
| Servo power | External appropriately rated rail; common logic ground |

The MCU output pin receives the servo signal only. Never power 24 servos from
the Mega 5 V pin or USB. Confirm RF module input-level tolerance; use level
translation on Mega/Uno SPI outputs if required by your module. Add supply
capacitors near the radio according to its module specification.

## Uno transmitter wiring

NRF CE D9, CSN D10, MOSI D11, MISO D12, SCK D13. Three analogue inputs A0/A1/A2
are X/Y/yaw; potentiometers connect between Uno 5 V and ground with wipers to ADC.
D4 to ground is the held deadman. D5 selects ripple, D6 selects wave; neither
selects tripod. D5 has priority if both are grounded. All switches use pullups.
Calibrate analogue centre and full-scale values in `axis()` for your joysticks.

## Six-axis arm model — measure before manufacture

The arm is a proposed chain, not a reconstruction from supplied arm measurements.
Base is at body [0,0,70] mm. Each joint rotates about its current local axis,
then translates by its local link vector **after rotation**:

| Joint | Axis | Link vector after rotation, mm | Function |
|---|---|---|---|
| J0 | Z | 0,0,50 | Base yaw / riser |
| J1 | Y | 90,0,0 | Shoulder |
| J2 | Y | 90,0,0 | Elbow |
| J3 | X | 25,0,0 | Wrist roll |
| J4 | Y | 30,0,0 | Wrist pitch |
| J5 | X | 35,0,0 | Tool roll / passive tool |

Nominal joint limits ±80 degrees; servo commands 10–170 degrees. Home is
[0,-20,50,0,-30,0] degrees. There is no active gripper or force feedback.
Collision geometry and payload-induced bending are not modelled. Start with a
light contact probe and a clear workspace. A printed bracket/CAD package is not
included because its dimensions and fasteners have not been supplied.

## Bring-up procedure

1. Disconnect servo power. Verify polarities, grounds, radio supply and switch
   behaviour. Build both firmware projects. Keep calibration flags false.
2. Support the body on a stand. Remove horns or mechanically disconnect one
   linkage at a time. Use the servo manufacturer's pulse/travel information.
3. Determine each joint's mathematical zero, electrical offset and direction.
   Mirror-mounted legs often need different signs; uniform signs in the JSON
   are illustrative. Measure safe end stops with clearance.
4. Update all 24 offsets, signs and bounds. Mirror absolute servo bounds into
   the receiver arrays `lo` and `hi`. Review the default 544–2400 us pulse mapping;
   narrow it to the servo's real specification if necessary.
5. Verify FK/IK against measured poses, not just simulation. Check leg neutral
   Z and arm link vectors. Pre-position supported joints to the commanded start
   pose; initial attachment is not rate-limited from measured shaft positions.
6. Set both hardware calibration gates true and upload the receiver again.
   Start host control with enable/deadman released. The startup disarm frame
   clears the software stop latch when the NC loop is healthy.
7. Enable briefly on the stand, check all channels, and test front sensor stop,
   host disconnect, transmitter loss and NC loop opening. Observe actual servo
   response, including possible loss of holding torque when signals detach.
8. Only then move to supported low-speed floor tests. Keep arm stowed, use a
   reachable physical servo-power disconnect and log each trial.

The NC loop is a software input; it is not a safety-rated emergency-stop circuit.
Cutting servo power is a separate hardware function. These interlocks do not
provide collision, current, thermal, tip-over or human-contact protection.
