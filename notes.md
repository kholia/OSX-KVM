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

Also tweaking the `smbios.plist` file can help (?).


### Change resolution in OpenCore

```diff
diff --git a/OpenCore-Catalina/config.plist b/OpenCore-Catalina/config.plist
index 4754e8c..489570f 100644
--- a/OpenCore-Catalina/config.plist
+++ b/OpenCore-Catalina/config.plist
@@ -692,7 +692,7 @@
                        <key>ConsoleMode</key>
                        <string></string>
                        <key>Resolution</key>
-                       <string>Max</string>
+                       <string>1920x1080</string>
                        <key>ClearScreenOnModeSwitch</key>
                        <false/>
                        <key>IgnoreTextInGraphics</key>
```

### FakeSMC installation

This option is not recommended. Building latest QEMU from Git repository is
recommended instead.

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

### Higher Resolution (UEFI + Clover)

Follow the steps below to get a higher resolution:

1. Set the desired Clover screen resolution in the relevant
   `config.plist.stripped.qemu` file and regenerate the corresponding
   `Clover*.qcow2` file (process documented in `Mojave/README.md`).

2. Ensure that the OVMF resolution is set equal to resolution set in your
   Clover.qcow2 file (default is 1024x768). This can be done via the OVMF menu,
   which you can reach with a press of the ESC button during the OVMF boot logo
   (before Clover boot screen appears). In the OVMF menu settings, set Device
   Manager -> OVMF Platform Configuration -> Change Preferred Resolution for Next
   Boot to the desired value (default is 1024x768). Commit changes and exit the
   OVMF menu.

3. Relaunch the boot script.

### Accelerated Graphics

Install VMsvga2 from [this location](https://sourceforge.net/projects/vmsvga2/). No support
is provided for this unmaintained project!

* Add `-vga vmware` to QEMU parameters in the booot script (e.g.
  boot-macOS.sh), if required.

* For Clover bootloader, add `wmv_option_fb=0x06` to the `<string>` tag of the
  `Arguments` key of the `config.plist` you use when generating the
  `CloverNG.qcow2`.

* See `UEFI/README.md` for GPU passthrough notes.

* Note: There is no working QXL driver for macOS so far.

### Virtual Sound Device

No support is provided for this. You are on your own. The sound output is known
to be choppy and distorted.

* Add `-device ich9-intel-hda -device hda-duplex` to the VM configuration.
  `boot-macOS.sh` already has this change.

* To get sound on your virtual Mac, install the VoodooHDA driver from
  [here](https://sourceforge.net/projects/voodoohda/files/).

Note: It seems that playback of Flash videos requires an audio device to be
present.

### Building QEMU from source

See http://wiki.qemu-project.org/Hosts/Linux for help.

```
$ git clone https://github.com/kholia/qemu.git

$ cd qemu

$ git checkout macOS

$ ./configure --prefix=/home/$(whoami)/QEMU --target-list=x86_64-softmmu --audio-drv-list=pa

$ make clean; make; make install
```

### Connect iPhone / iPad to macOS guest

Some folks are using https://www.virtualhere.com/ to connect iPhone / iPad to
the macOS guest.

Update: It appears that VirtualHere doesn't work on modern macOS versions.

Please passthrough a PCIe USB card to the virtual machine to be able to connect
iDevices to it.

### Exposing AES-NI instructions to macOS

Add `+aes` argument to the `-cpu` option in `boot-macOS.sh` file.

``` diff
diff --git a/boot-macOS.sh b/boot-macOS.sh
index 5948b8a..3acc123 100755
--- a/boot-macOS.sh
+++ b/boot-macOS.sh
@@ -18,7 +18,7 @@
 # Use "-device usb-tablet" instead of "-device usb-mouse" for better mouse
 # behaviour. This requires QEMU >= 2.9.0.

-qemu-system-x86_64 -enable-kvm -m 3072 -cpu Penryn,kvm=off,vendor=GenuineIntel \
+qemu-system-x86_64 -enable-kvm -m 3072 -cpu Penryn,kvm=off,vendor=GenuineIntel,+aes \
          -machine pc-q35-2.4 \
          -smp 4,cores=2 \
          -usb -device usb-kbd -device usb-mouse \
```

Other host CPU features can be similarly exposed to the macOS guest.

The following command can be used on macOS to verify that AES-NI instructions are exposed,

```
sysctl -a | grep machdep.features
```

On machines with OpenSSL installed, the following two commands can be used to
check AES-NI performance,

```
openssl speed aes-128-cbc

openssl speed -evp aes-128-cbc  # uses AES-NI
```

### Exposing AVX and AVX2 instructions to macOS

Exposing AVX and AVX2 instructions to macOS requires support for these
instructions on the host CPU.

The `boot-clover.sh` script already exposes AVX and AVX2 instructions to the
macOS guest by default. Modify or comment out the `MY_OPTIONS` line in
`boot-clover.sh` file in case you are having problems.

To enable AVX2, do the following change,

`Clover boot menu -> Options -> Binaries patching -> Fake CPUID -> 0x0306C0  # for Haswell`

For details, see [this wiki](https://clover-wiki.zetam.org/Configuration/KernelAndKextPatches) page.

Once enabled, the following commands can be used to confirm the presence of AVX
and AVX2 instructions on the macOS guest.

```
$ sysctl -a | grep avx
hw.optional.avx2_0: 1
hw.optional.avx1_0: 1

$ sysctl -a | grep leaf7
machdep.cpu.leaf7_features: SMEP BMI1 AVX2 BMI2
machdep.cpu.leaf7_feature_bits: 424
```

### Running Docker for Mac

Docker for Mac requires enabling nested virtualization on your host machine,

```
modprobe -r kvm_intel
modprobe kvm_intel nested=1
```

Also you have to add `vmx,rdtscp` arguments to the `-cpu` option in
`boot-macOS.sh` file.

### Using virtio-net-osx with macOS

Configuration options for macOS Sierra (thanks to virtio-net-osx project users),

```
-netdev user,id=hub0port0 \
-device virtio-net,netdev=hub0port0,id=eth0 \
-set device.eth0.vectors=0
```

Adapt these to your use case. These changes need to be made in the `boot-*`
scripts. On the guest, install the included `Virtio-Net-Driver-0.9.4.pkg`
package.

Update: This is no longer recommended. Use `vmxnet3` adapter instead.

### Using virtio-blk-pci with macOS

Newer macOS (namely Mojave+) have support for some virtio drivers.

This can be enabled by applying the following change to `boot-macOS-NG.sh` to
get some performance gain.

```diff
-         -device ide-hd,bus=sata.4,drive=MacHDD \
+         -device virtio-blk-pci,drive=MacHDD \
```

### Boot Notes

Type the following after boot,

```
"KernelBooter_kexts"="Yes" "CsrActiveConfig"="103"
```

### SIP notes

Disable/enable System Integrity Protection (SIP),

- Boot into Clover EFI Menu

- Select Options (gear icon) using arrow keys

- Select System Parameters

- Select System Integrity Protection

- Change to enable/disable

  - Disable SIP - Check: Allow Untrusted Kexts, Allow Unrestricted FS, Allow
    Task for PID, Allow Unrestricted Dtrace, Allow Unrestricted NVRAM
  - Enable SIP - Uncheck everything

- Select Return (multiple times as needed)

- Boot macOS partition

These instructions are borrowed from https://hackintosher.com/ forums.

To make this change permanent, use `Clover Configurator` to change
`CsrActivateConfig` in `config.plist`.

### Permission problems with libvirt / qemu?

```
sudo setfacl -m u:libvirt-qemu:rx <path>  # fix virt-manager perm problems
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

* Put "org.chameleon.Boot.plist" in /Extra folder.

* System Preferences -> Sharing -> enable Screen Sharing and Remote Login

* System Preferences -> Energy Saver -> Computer sleep set to Never

* System Preferences -> Energy Saver -> Display sleep set to Never

* If you are unable to wake Mojave from sleep using mouse or keyboard, you can
  manually wake the VM up from sleep from the QEMU prompt by using the
  `system_wakeup` command,

  ```
  (qemu) system_wakeup
  (qemu)
  ```

  However, macOS crashes on wakeup.


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

### Clover References

* https://clover-wiki.zetam.org/Development

* https://sourceforge.net/p/cloverefiboot/code/HEAD/log/?path=
