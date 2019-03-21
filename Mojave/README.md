### Notes

Mojave installs the same way as [High Sierra](../HighSierra/README.md). The
only difference is that Mojave now requires CPU instructions that were
introduced with Nehalem, so you will need to add CPU feature flags for ssse3,
sse4.2, and popcnt to avoid Illegal Instruction crashes in the graphics
subsystem after boot is complete (causing the top menu bar to flash on and off,
and Finder to crash on open).

Tested macOS Mojave 10.14.4 with Clover 4843 (from 2019-01-09). Note: Higher
Clover versions are "broken".

Note: Use `create_iso_mojave.sh` for generating a macOS Mojave based ISO image.

Note: Use 64-bit Ubuntu 18.04.2 LTS as the host for "best" results.
