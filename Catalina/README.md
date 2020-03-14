### Notes

Catalina installs the same way as [Mojave](../Mojave/README.md).

Tested with macOS Catalina 10.15 with Clover 5070 (from October, 2019).

Note: Use `create_iso_catalina.sh` for generating a macOS Catalina based ISO
image.

Notes:

Use 64-bit Ubuntu 18.04.2 LTS as the host for "best" results.

`rm -f CloverNG.qcow2; sudo ./clover-image-ng.sh --iso Clover-v2.5k-5070-X64.iso --cfg clover/config.plist.stripped.qemu --img CloverNG.qcow2`

`rm -f CloverNG.qcow2; sudo ./clover-image-ng.sh --iso Clover-5105-X64.iso --cfg config.plist --img CloverNG.qcow2`

The `modern` installation method (borrowed from https://github.com/foxlet/macOS-Simple-KVM) requires an internet connection
(during macOS installation) to work.

### Links

* https://github.com/PassthroughPOST/Hackintosh-KVM/blob/master/config.plist
