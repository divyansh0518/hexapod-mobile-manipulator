# Validation record

Software checks executed for this archive on 2026-11-02.

- Environment: Python 3.14.6, NumPy 2.5.1, Darwin arm64.
- `python -m unittest discover -s tests -v`: **10 tests passed**.
- All three gait CLI runs: 10 simulated seconds each, 50 Hz, 500 frames per CSV.
- Arm CLI demo: target [220,20,150] mm; FK of solved command within 0.415 mm
  of target (numerical model only).
- Reference geometry, dense gait FK/IK round trips, nominal servo bounds,
  ideal support geometry, gait continuity, six-axis pose IK, invalid inputs,
  protocol CRC, motion speed limit and inhibition paths checked.
- No hardware testing, real radio range, K10 runtime, model inference benchmarks,
  torque, terrain or real arm accuracy measurements performed.
- AVR toolchain compilation has **not** been executed for this release. The
  included CI jobs build both PlatformIO firmware projects when uploaded.
  Check the actual CI result before flashing.

## Included sample simulation traces

| Gait | Frames | Minimum ideal support margin (mm) | Minimum stance legs |
|---|---:|---:|---:|
| ripple | 500 | 154.78 | 4 |
| tripod | 500 | 150.48 | 3 |
| wave | 500 | 157.31 | 5 |

These are ideal scheduled contacts and an assumed centred COM. They do not
validate physical stability or dynamics, and servo slew can make commanded
foot locations lag the ideal trajectory. The arm test tolerance is a solver
criterion, not a measured machining/servo accuracy.

## Reproduce

From project root after installing the package:

```bash
python -m unittest discover -s tests -v
hexapod simulate --gait tripod --seconds 10 --output logs/tripod.csv
hexapod simulate --gait ripple --seconds 10 --output logs/ripple.csv
hexapod simulate --gait wave --seconds 10 --output logs/wave.csv
hexapod arm-demo --target 220 20 150
```

SHA256SUMS.txt records every packaged source/document/data file except itself.
The original Downloads path became unavailable after its first read; the
reference source text is preserved from that captured read, with provenance
noted separately. Do not interpret this archive as an original hardware-build
record or a byte-certified copy of the lost source file.
