# Third-party notices

## Supplied Arduino reference

Original file: `reference/Hexapod_Arduino.ino`.
Header credits: Özgür Toprak Önsoy and Emre Kalem, November 2025, Eskişehir, Türkiye.
Copyright 2025 Emre Kalem. License: MIT; full text retained in the file and LICENSE.
Geometry, pin ordering and baseline kinematics informed this release. The new
work does not remove the requirement to retain the original notice.

## External runtime dependencies (not vendored)

- NumPy — BSD-3-Clause: https://numpy.org/doc/stable/license.html
- pyserial — BSD-3-Clause: https://github.com/pyserial/pyserial/blob/master/LICENSE.txt
- OpenCV — see distribution license: https://opencv.org/license/
- ONNX Runtime — MIT: https://github.com/microsoft/onnxruntime/blob/main/LICENSE
- Arduino Servo — LGPL-2.1: https://github.com/arduino-libraries/Servo
- RF24 — GPL-2.0: https://github.com/nRF24/RF24
- PlatformIO Core — Apache-2.0: https://github.com/platformio/platformio-core
- UNIHIKER vendor MicroPython/AI modules — obtained from vendor firmware, not
  included or relicensed by this archive; consult the vendor distribution terms.

Python sources and original project documentation are offered under MIT. AVR
firmware source files are additionally made available under GPL-2.0-or-later so
that a combined firmware build using RF24 can be redistributed under compatible
terms. See firmware/LICENSE-NOTE.md. Dependency obligations still apply when
redistributing compiled artifacts. This archive includes no compiled firmware,
vendor libraries, trained model weights or datasets.

Vendor AI API references and lab URLs are linked in the documentation. The AI
script is an original integration against documented APIs, not a bundled vendor
example or a claim of custom-model development.
