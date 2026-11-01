# Publish the extracted project when ready

No Git repository was initialized and nothing was uploaded by the archive creator.
The ZIP includes `.github/workflows/` but contains no `.git` directory.

1. Extract the ZIP and open the `hexapod-mobile-manipulator` directory.
2. Add your real photo/video and replace README media links.
3. Review the status table, credit your actual work and update measured results.
4. Create an empty repository in your own GitHub account through the website.
5. Upload this folder's contents, including hidden `.github` workflow files.
   The GitHub web upload UI may omit hidden folders depending on the OS; use
   GitHub Desktop if needed. Keep README.md at the repository root.
6. Let CI run and inspect both Python tests and firmware compilation. A supplied
   workflow is not evidence of a passing run until GitHub executes it.

Suggested name: `hexapod-mobile-manipulator`.
Suggested description: `Bio-inspired hexapod locomotion and six-axis manipulation:
Python kinematics, NRF24 teleoperation, K10 vision integration and experiments.`
Suggested topics: `hexapod`, `bio-inspired-robotics`, `mobile-manipulation`,
`inverse-kinematics`, `arduino-mega`, `gait-generation`, `nrf24l01`, `unihiker`.
Do not commit serial port credentials, private camera URLs or large raw videos.
