# Provenance and implementation boundaries

`reference/Hexapod_Arduino.ino` preserves the source text read from the supplied file.
The Downloads file became unavailable during packaging, so the reference was
reconstructed from that captured text; byte-for-byte identity is not certified. It identifies Özgür Toprak Önsoy and Emre Kalem, dated November 2025, and
contains the MIT notice with copyright 2025 Emre Kalem. No source repository URL
was supplied; no origin URL has been invented.

Retained source facts: three link lengths (38,86.25,160.5 mm), six mounting
coordinates, RF/RM/RR/LR/LM/LF order, the 18 leg signal pins, and the negative-knee
FK/IK convention. The new gait module generalizes the alternating tripod concept.
The reference's original radio payload and its startup behaviour are not reused.

New integration choices: Mega + Python host split, 16-byte radio packet,
56-byte serial frame, servo calibration map, watchdog/interlock paths, the
six-revolute arm chain, K10 event script, host detector/projection functions,
software tests and experiment documentation. Arm lengths, limits, power system,
camera transforms and neutral stance are assumptions until measured.

The generated software was authored as a project scaffold with AI assistance.
Hardware design, calibration, physical testing, original construction and
performance remain the project owner's responsibility to document accurately.

## Evidence levels

- **Supplied source:** geometry/pins and original Arduino code only.
- **Software checked:** see VALIDATION.md for executed checks and their scope.
- **Unverified integration:** Arduino toolchain build if not executed locally,
  real K10 APIs/firmware behaviour, wiring, servo calibration and collision clearance.
- **Unmeasured performance:** radio range, latency, AI accuracy/FPS, walking
  stability/terrain success, arm load capacity, runtime and real manipulation.
