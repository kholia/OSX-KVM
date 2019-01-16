### Notes

Mojave installs the same way as [High Sierra](../HighSierra/README.md). The
only difference is that Mojave now requires CPU instructions that were
introduced with Nehalem, so you will need to add CPU feature flags for ssse3,
sse4.2, and popcnt to avoid Illegal Instruction crashes in the graphics
subsystem after boot is complete (causing the top menu bar to flash on and off,
and Finder to crash on open). You may also need to disable system sleep in
Mojave’s Energy Saver settings because that a Mojave system will halt and not
respond to any wake-ups after the system sleep.

Tested with Clover 4674.

Note: Use `create_iso_mojave.sh` for generating a macOS Mojave based ISO image.
