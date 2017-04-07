### App Store problems

Do you see the "Your device or computer could not be verified" message when you
try to login to the App Store? If yes, here are the steps to fix it.

* Make sure that your wired ethernet connection is called "en0" (and not "en1" or
something else). Use "ifconfig" command to verify this.

* If the wired ethernet connection is not called "en0", then then go to Network
in System Preferences and delete all the devices, and apply the changes. Next,
delete /Library/Preferences/SystemConfiguration/NetworkInterfaces.plist file.
Finally reboot, and then use the App Store without problems.

This fix was found by Glnk2012 of https://www.tonymacx86.com/ site.

Also tweaking the `smbios.plist` file using `Chameleon Wizard` can help with
App Store problems.

### Enoch Bootloader

* Download Enoch bootloader from http://www.insanelymac.com/forum/ (requires
  registration).

* Using Pacifist open the “Enoch-rev.####.pkg” file and extract the file called
  "boot" from Core.pkg/usr/standalone/i386/boot

* Rename boot to enoch_rev####_boot.


### FakeSMC installation

* Do the following steps as `root` user on the Virtual Machine (VM).

  ```
  cp -a FakeSMC.kext /System/Library/Extensions/
  cd /System/Library/Extensions/
  chmod -R 755 FakeSMC.kext
  chown -R root:wheel FakeSMC.kext
  rm -R /System/Library/Caches/com.apple.kext.caches
  touch /System/Library/Extensions && kextcache -u /  # optional step
  ```

* Remove the `-device isa-applesmc,osk=... \` line completely from `boot*.sh` file(s).

* If you are using the `virsh` boot method, then remove the following lines from your `virsh` XML file,

  ```
  <qemu:arg value='-device'/>
  <qemu:arg value='isa-applesmc,osk=XXX'/>
  ```

* Reboot the VM for changes to take effect. Use `kextstat` to verify that `FakeSMC.kext` is loaded.

* Latest `FakeSMC.kext` version can be downloaded from [this location](https://bitbucket.org/RehabMan/os-x-fakesmc-kozlek).

* If your updated VM is failing to boot and it doesn't have `FakeSMC.kext` installed, the following steps can used to inject `FakeSMC.kext` into the VM disk image,

  ```
  $ sudo modprobe nbd  # all steps to be executed on the QEMU/KVM host

  $ sudo qemu-nbd -c /dev/nbd0 -n mac_hdd.img

  $ sudo fdisk -l /dev/nbd0
  ...
  Device          Start       End   Sectors   Size Type
  /dev/nbd0p1        40    409639    409600   200M EFI System
  /dev/nbd0p2    409640 132948151 132538512  63.2G Apple HFS/HFS+
  /dev/nbd0p3 132948152 134217687   1269536 619.9M Apple boot

  $ sudo kpartx -a /dev/nbd0

  $ mkdir mnt

  $ sudo mount -t hfsplus -o force,rw /dev/mapper/nbd0p2 mnt

  $ cd mnt

  $ ls
  Applications  bin  Chameleon.Backups  cores  dev  etc...

  # Install FakeSMC.kext using the above mentioned steps

  $ cd ..

  $ sudo umount mnt

  $ sudo kpartx -d /dev/nbd0

  $ sudo qemu-nbd -d /dev/nbd0
  ```

### Enoch Bootloader (alternate extraction method)

* Build xar from http://mackyle.github.io/xar/ on a Linux box.

* Extract "boot" from using the following steps,

  ```
  xar -x -f Enoch-rev.2848.pkg

  gunzip -c Core.pkg/Payload | cpio -i

  cp usr/standalone/i386/boot enoch_rev2848_boot
  ```

### Higher Resolution

If you want a larger VNC screen add the following to the bootloader config in /Extra/org.chameleon.Boot.plist:

```
<key>Graphics Mode</key>
<string>1440x900x32</string>
```

Make sure to pick a resolution that is supported by the SeaBIOS used by QEMU.
The full list can be found in the source for SeaBIOS located
[here](http://git.qemu-project.org/?p=seabios.git;a=blob_plain;f=vgasrc/bochsvga.c;hb=HEAD).

For example, setting the resolution to 2560x1440x32 will not work. OS X will
boot with the next lowest supported resolution which is 1920x1200x32. Instead,
use 2560x1600x32 and it will work.

### Accelerated Graphics

Install VMsvga2 from [this location](https://sourceforge.net/projects/vmsvga2/). No support
is provided for this unmaintained project!

* Add `-vga vmware` to QEMU parameters in boot-macOS.sh.

* Add the following to `/Extra/org.chameleon.Boot.plist` file.

  ```
  <key>Kernel Flags</key>
  <string>vmw_options_fb=0x06</string>
  ```

Thanks to Zhang Tong and Kfir Ozer for finding this.

GPU passthrough is out of scope for this project. No support for it is provided
whatsoever.

### Virtual Sound Device

No support is provided for this. You are on your own. The sound output is known
to be choppy and distorted.

* Add `-device ich9-intel-hda -device hda-duplex` to the VM configuration.
  `boot-macOS.sh` already has this change.

* To get sound on your virtual Mac, install the VoodooHDA driver from
  [here](https://sourceforge.net/projects/voodoohda/files/).


### Building QEMU from source

See http://wiki.qemu-project.org/Hosts/Linux for help.

```
$ git clone https://github.com/qemu/qemu.git

$ cd qemu

$ ./configure --prefix=/home/$(whoami)/QEMU --target-list=x86_64-softmmu --audio-drv-list=pa

$ make clean; make; make install
```

### Boot Notes

Type the following after boot,

```
"KernelBooter_kexts"="Yes" "CsrActiveConfig"="103"
```

### Kernel Extraction (older alternate to "pbzx" method)

* Install Pacifist on OS X.

* Mount "InstallESD.dmg" file.

* With Pacifist browse to the above volume (use the "Open Apple Installers"
  menu option) and then open "Essentials.pkg". Extract the folder & file
  (Kernels/kernel) located at /System/Library/Kernels/kernel location.

* After extracting the Kernels folder, place it in the same directory as the
  ISO creation script.


### Post Installation

Put "org.chameleon.Boot.plist" in /Extra folder.


### Installer Details (InstallESD.dmg)

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

Move 'InstallESD.dmg' to '/Applications/Install macOS Sierra.app/Contents/SharedSupport/' location (for macOS Sierra).
