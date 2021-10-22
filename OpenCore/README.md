### Notes

Catalina installs the same way as Mojave.

Tested with macOS Big sur with OpenCore-0.7.4-RELEASE.zip release in October,
2021.

Note: Use `create_iso_catalina.sh` for generating a macOS Catalina based "ISO"
(actually DMG) image.

Attention: Use 64-bit Ubuntu 20.04 LTS or later as the host OS for "best"
results. Guestfish output results may vary across platforms.

```
# Normal OpenCore Image
rm -f OpenCore.qcow2; sudo ./opencore-image-ng.sh --cfg config.plist --img OpenCore.qcow2
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
