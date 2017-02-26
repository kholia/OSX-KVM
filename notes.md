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

### Enoch Bootloader

* Download Enoch bootloader from http://www.insanelymac.com/forum/ (requires
  registration).

* Using Pacifist open the “Enoch-rev.####.pkg” file and extract the file called
  "boot" from Core.pkg/usr/standalone/i386/boot

* Rename boot to enoch_rev####_boot.


### Enoch Bootloader (alternate extraction method)

* Build xar from http://mackyle.github.io/xar/ on a Linux box.

* Extract "boot" from using the following steps,

  ```
  xar -x -f Enoch-rev.2848.pkg

  gunzip -c Core.pkg/Payload | cpio -i

  cp usr/standalone/i386/boot enoch_rev2848_boot
  ```

### Higher Resolution

If you want a larger VNC screen add the following to the bootloader config in /Extra/org.chameleon.boot.plist:

```
<key>Graphics Mode</key>
<string>1440x900x32</string>
```

Make sure to pick a resolution that is supported by the SeaBIOS used by QEMU. The full list can be found in the source for SeaBIOS located here: http://git.qemu-project.org/?p=seabios.git;a=blob_plain;f=vgasrc/bochsvga.c;hb=HEAD

For example, setting the resolution to 2560x1440x32 will not work. OSX will boot with the next lowest supported resolution which is 1920x1200x32. Instead, use 2560x1600x32 and it will work.

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

Put "org.chameleon.boot.plist" in /Extra folder.


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
