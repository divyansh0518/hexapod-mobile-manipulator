# Research positioning and portfolio wording

The strongest presentation explains a design decision, its implementation and
its measured consequence. Use the following research connections as motivation,
not affiliation, endorsement, or a claim of matching a lab's current openings.

| Research direction | Connection to this platform | A useful next experiment |
|---|---|---|
| Computational robot design and fabrication | Leg geometry, mount placement and arm mass jointly shape feasible behaviour | Sweep morphology parameters, fabricate one variation, compare predictions with walking trials |
| Robust manipulation and control | Target uncertainty and arm/base coupling affect reach accuracy | Compare position-only and full-pose control, quantify repeatability under load |
| Gait and balance for assistive robotics | Contact sequencing and support margins offer a small-scale control study | Measure combined COM and body tilt during gait/arm transitions |

[CREATE](https://www.epfl.ch/labs/create/) and EPFL's
[robotics expertise directory](https://www.epfl.ch/research/domains/robotics/our-experts/)
provide a relevant connection to computational design and bio-inspired systems.
[LASA](https://www.epfl.ch/labs/lasa/) provides a connection to manipulation and
robot learning/control. [REHAssist](https://www.epfl.ch/labs/rehassist/) lists
locomotion assistance, balance and rehabilitation among its topics. These are
inferred technical connections; this prototype is neither a soft robot nor a
rehabilitation device and does not implement learning from demonstration.

Do not claim a lab is less competitive, newly formed or more likely to provide
attention without current evidence. An application is stronger when it points
to your specific contribution and one experiment you would like to pursue.

## Software-stage portfolio description

**Hexapod Robot with a Six-Axis Manipulator — Bio-Inspired Mobile Manipulation**

- Developed a modular software architecture for a 24-joint platform combining
  an 18-joint hexapod body with a proposed six-axis serial manipulator, using
  source-backed leg geometry and configurable actuator calibration.
- Implemented insect-inspired tripod, ripple and wave gait scheduling with
  analytic leg kinematics and ideal support-polygon analysis to explore the
  tradeoff between contact redundancy and locomotion speed.
- Added constrained numerical arm IK and target-directed approach logic,
  linking K10 native visual identification to surveyed targets and providing
  an optional calibrated host-side detection pipeline.
- Designed NRF24 teleoperation firmware with deadman control, CRC-framed joint
  commands, communication watchdogs and a range-based inhibition path, alongside
  an independent FPV integration and validation plan.

These bullets describe software work and design intent. After physically
validating the build, replace them with what **you** built and measured. State
upstream reuse clearly. Use the original request's stronger claims (terrain
adaptation, real-time custom AI, low latency, 1 km range) only when supported by
your logs, setup details and footage. Do not add invented metrics.

## Interview discussion prompts

Why three joints per leg? Which support assumptions fail as the arm moves?
Why separate native K10 identification from geometric localization? What happens
when the radio link or servo power fails? Which measurement most changes the
next mechanical design? Discussing these tradeoffs is more persuasive than
adding keywords without implementation evidence.
