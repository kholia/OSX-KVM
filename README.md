Host
----

Ubuntu 15.10 running on i5-6500 CPU.

Fedora 24 running on i5-6500 CPU.

Tested with QEMU 2.4.1 and QEMU 2.5.

ISO Creation
------------

* Run the ISO creation script, making sure to use 'sudo' if possible.

* Copy the ISO from your Mac to your KVM machine.

Enoch Bootloader
----------------

* Download Enoch bootloader from http://www.insanelymac.com/forum/ (requires
  registration).

* Using Pacifist open the “Enoch-rev.####.pkg” file and extract the file called
  "boot" from Core.pkg/usr/standalone/i386/boot

* Rename boot to enoch_rev####_boot.

Installation
------------

```bash
virsh --connect qemu:///system define osx-libvirt-install.xml

```

Redefine HDD/DVD sources in virt-manager

References
----------

* https://github.com/Karlson2k/k2k-OSX-Tools

* https://macosxvirtualmachinekvm.wordpress.com/guide-mac-os-x-10-11-el-capitan-vm-on-unraid/

* http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/

* http://bit.do/bootable
