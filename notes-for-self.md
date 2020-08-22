### USB passthrough notes

#### USB 3.0 flash drive

The following USB configuration works for usb passthrough of a USB 3.0 flash
drive to Fedora 25 guest.

    -device nec-usb-xhci,id=xhci \
    -device usb-host,bus=xhci.0,vendorid=0x0781,productid=0x5590 \
    -usb -device usb-mouse,bus=usb-bus.0 -device usb-kbd,bus=usb-bus.0 \
    ...

#### Moto G3 phone

The following USB configuration works for usb passthrough of a Moto G3 phone to
Fedora 25 guest.

    -device usb-host,bus=usb-bus.0,vendorid=0x22b8,productid=0x002e \
    -usb -device usb-mouse,bus=usb-bus.0 -device usb-kbd,bus=usb-bus.0 \
    ...

#### CoolerMaster keyboard

The following USB configuration works for usb passthrough of a CoolerMaster
keyboard to macOS Sierra guest!

    -device usb-host,bus=usb-bus.0,vendorid=0x2516,productid=0x0004 \
    -usb -device usb-tablet,bus=usb-bus.0 -device usb-kbd,bus=usb-bus.0 \
    ...


#### Virtual USB disk

The following USB configuration works for attaching a virtual USB disk to macOS
Sierra guest. Use "qemu-img" to create "disk.raw" virtual disk.

    -drive if=none,id=usbstick,file=disk.raw,format=raw \
    -device usb-storage,bus=usb-bus.0,drive=usbstick \
    ...

However USB passthrough of EHCI, and XHCI (USB 3.0) devices does not work with
macOS Sierra. See https://bugs.launchpad.net/qemu/+bug/1509336 for
confirmation. According to this bug report, USB passthrough does not work with
versions >= Mac OS X El Capitan guests.

It seems that this problem can be fixed by using OVMF + Clover.

Update: OVMF + Clover doesn't help. It seems that macOS is missing the required
drivers for the EHCI, and XHCI controllers that are exposed by QEMU.
