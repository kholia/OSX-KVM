### Notes

Catalina installs the same way as [Mojave](../Mojave/README.md).

Tested with macOS Catalina 10.15.7 with OpenCore-0.6.2-DEBUG.zip release.

Note: Use `create_iso_catalina.sh` for generating a macOS Catalina based "ISO"
(actually DMG) image.

Attention: Use 64-bit Ubuntu 20.04 LTS as the host OS for "best" results.
Guestfish output results may vary across platforms.

```
cp -a ../resources/OcBinaryData/Resources EFI/OC/Resources  # symlink hacks don't work

# Normal OpenCore Image
rm -f OpenCore.qcow2; sudo ./opencore-image-ng.sh --cfg config.plist --img OpenCore.qcow2

# OpenCore w/ ShowPicker Disabled
rm -f OpenCore-nopicker.qcow2; sudo ./opencore-image-ng.sh --cfg config-nopicker.plist --img OpenCore-nopicker.qcow2

# Passthrough Optimized OpenCore
rm -f OpenCore-Passthrough.qcow2; sudo ./opencore-image-ng.sh --cfg config-pt.plist --img OpenCore-Passthrough.qcow2
```

Note: https://github.com/thenickdude/KVM-Opencore is one of the best resources
for customizing `OpenCore.qcow2`. Thanks Nick! :)

### Links

* https://github.com/acidanthera/OpenCorePkg/releases

* https://github.com/williambj1/OpenCore-Factory/releases

* https://opencore.slowgeek.com/ (neat!)

* https://github.com/chris1111/USB-3.0-NEC/releases (thanks Chris!)

* https://github.com/khronokernel/Opencore-Vanilla-Desktop-Guide/blob/master/clover-conversion/clover-efi.md

* https://insanelymacdiscord.github.io/Getting-Started-With-OpenCore/

* https://dortania.github.io/Anti-Hackintosh-Buyers-Guide/

* https://dortania.github.io/OpenCore-Desktop-Guide/troubleshooting/debug.html
