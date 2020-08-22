### Notes

Tested with macOS Big Sur `DeveloperSeed` with OpenCore-0.6.0-DEBUG.zip
(snapshot).

- https://github.com/williambj1/OpenCore-Factory/releases

- https://github.com/acidanthera/OpenCorePkg/releases

Attention: Use 64-bit Ubuntu 20.04 LTS as the host OS for "best" results.
Guestfish output results may vary across platforms.

```
git submodule update --init --recursive

cp -a ../resources/OcBinaryData/Resources EFI/OC/Resources  # symlink hacks don't work

rm -f OpenCore.qcow2; sudo ./opencore-image-ng.sh --cfg config.plist --img OpenCore.qcow2
```

Note: https://github.com/thenickdude/KVM-Opencore is one of the best resources
for customizing `OpenCore.qcow2`. Thanks Nick! :)
