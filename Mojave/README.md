### Notes

Mojave installs the same way as [High Sierra](../HighSierra/README.md). The
only difference is that Mojave now requires CPU instructions that were
introduced with Nehalem, so you will need to add CPU feature flags for ssse3,
sse4.2, and popcnt to avoid Illegal Instruction crashes in the graphics
subsystem after boot is complete (causing the top menu bar to flash on and off,
and Finder to crash on open).

Tested with macOS Mojave 10.14.4 with Clover 4934 (from May, 2019).

Note: Use `create_iso_mojave.sh` for generating a macOS Mojave based ISO image.

Note: Use 64-bit Ubuntu 18.04.2 LTS as the host for "best" results.

Old:

`rm -f Clover.qcow2; sudo ./clover-image.sh --iso Clover-v2.4k-4934-X64.iso --cfg clover/config.plist.stripped.qemu --img CloverNG.qcow2`

Modern:

`rm -f CloverNG.qcow2; sudo ./clover-image-ng.sh --iso Clover-v2.5k-5070-X64.iso --cfg clover/config.plist.stripped.qemu --img CloverNG.qcow2`

The `modern` installation method (borrowed from https://github.com/foxlet/macOS-Simple-KVM) requires an internet connection
(during macOS installation) to work.

As indicated in `ideas.md`, there is a way to overcome this (final) limitation.
