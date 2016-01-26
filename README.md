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

Enoch Bootloader
----------------

* Download Enoch bootloader from http://www.insanelymac.com/forum/ (requires
  registration).

* Using Pacifist open the “Enoch-rev.####.pkg” file and extract the file called
  "boot" from Core.pkg/usr/standalone/i386/boot

* Rename boot to enoch_rev####_boot.

Post Installation
-----------------

Put "org.chameleon.boot.plist" in /Extra folder.

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
