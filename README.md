Host
----

Ubuntu 15.10 running on i5-6500 CPU.

Fedora 24 running on i5-6500 CPU.

Tested with QEMU 2.4.1 and QEMU 2.5.

Notes
-----

* Type the following after boot,
  "KernelBooter_kexts"="Yes" "CsrActiveConfig"="103"

Kernel Extraction
-----------------

* Install Pacifist on OS X.

* Mount "InstallESD.dmg" file.

* With Pacifist browse to the above volume (use the "Open Apple Installers"
  menu option) and then open "Essentials.pkg". Extract the folder & file
  (Kernels/kernel) located at /System/Library/Kernels/kernel location.

ISO Creation
------------

* After extracting the Kernels folder, place it in the same directory as the iso creation script.

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
virsh --connect qemu:///system define osx-libvirt.xml

```

Redefine HDD/DVD sources in virt-manager

Post Installation
-----------------

Put "org.chameleon.boot.plist" in /Extra folder.

```bash
sudo modprobe nbd
sudo qemu-nbd -c /dev/nbd0 /some/image.qcow2
sudo mkdir -p /mnt/osx-kvm
sudo mount -t hfsplus -o force,rw /dev/nbd0p2 /mnt/osx-kvm
sudo mkdir /mnt/osx-kvm/Extra
sudo cp org.chameleon.boot.plist /mnt/osx-kvm/Extra
sudo umount /mnt/osx-kvm
sudo qemu-nbd -d /dev/nbd0
```

InstallESD.dmg
--------------

```
Name: Mac OS X El Capitan
Version: 10.11.1 (15B42) InstallESD
Mac Platform: Intel

Untouched InstallESD.dmg file from the full 10.11.1 (Build 15B42) installer.
"Install OS X El Capitan.app/Contents/SharedSupport/InstallESD.dmg"
MD5: 3332a4e05713366343e03ee6777c3374
Release Date: October 21, 2015
```

``jar -xf <zipfile>`` is pretty neat.

Move 'InstallESD.dmg' to '/Applications/Install OS X El Capitan.app/Contents/SharedSupport/InstallESD.dmg' location.

References
----------

* https://github.com/Karlson2k/k2k-OSX-Tools

* https://macosxvirtualmachinekvm.wordpress.com/guide-mac-os-x-10-11-el-capitan-vm-on-unraid/

* http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/

* http://bit.do/bootable
