### Notes

Catalina installs the same way as [Mojave](../Mojave/README.md).

Tested with macOS Catalina 10.15 with OpenCore-0.5.7-RELEASE.zip (from April, 2020).

Note: Use `create_iso_catalina.sh` for generating a macOS Catalina based ISO
image.

Notes:

Use 64-bit Ubuntu 18.04.2 LTS as the host for "best" results.

```
rm -f CloverNG.qcow2; rm -f OpenCore.qcow2 ;sudo ./clover-image-ng.sh  --cfg config.plist --img OpenCore.qcow2
```

### Links

* https://github.com/acidanthera/OpenCorePkg/releases

* https://opencore.slowgeek.com/ (neat!)

* https://github.com/khronokernel/Opencore-Vanilla-Desktop-Guide/blob/master/clover-conversion/clover-efi.md

* https://khronokernel-2.gitbook.io/opencore-vanilla-desktop-guide/ktext

* https://insanelymacdiscord.github.io/Getting-Started-With-OpenCore/

* https://dortania.github.io/Anti-Hackintosh-Buyers-Guide/
