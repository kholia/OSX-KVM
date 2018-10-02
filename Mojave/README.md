### Notes

Mojave installs the same way as High Sierra. The only difference is that Mojave now requires
CPU instructions that were introduced with Nehalem, so you will need to add CPU feature
flags for ssse3, sse4.2, and popcnt to avoid Illegal Instruction crashes in the graphics
subsystem after boot is complete (causing the top menu bar to flash on and off, and Finder
to crash on open).

Tested with Clover 4674.
