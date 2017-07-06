### Note

See the [debugging section below](https://github.com/kholia/OSX-KVM#debugging)
and closed issues before opening a new issue.

### Host System Details

Known to work on:

* Ubuntu 15.10 running on i5-6500 CPU.

* Ubuntu 16.10 running on i7-3960X CPU.

* Fedora 24 running on i5-6500 + i7-6600U CPU.

Tested with QEMU 2.4.1, 2.5, 2.6.1, and 2.8.

AMD CPU(s) are known to be problematic. AMD FX-8350 works but Phenom II X3 720
does not. A CPU with SSE4.1 support is required for macOS Sierra.

Intel VT-x / AMD SVM is required.

### Installation Preparation

#### Preparation steps on your current OS X / macOS

* Download OS X El Capitan or macOS Sierra installer from Apple App Store.

* Clone this repository. Files included in this repository are needed for ISO
  creation.

  ```
  git clone https://github.com/kholia/OSX-KVM.git
  ```

* Run the ISO creation script `create_install_iso.sh` included in this
  repository. Run it with `sudo`.

  This script supports specifying the path to OS X / macOS installation
  application manually via the `-a` option.

* Copy the generated ISO from your Mac to your QEMU/KVM machine.

#### Preparation steps on your QEMU system

* Clone this repository again on your QEMU system. Files from this repository are used in the following steps.

* Install QEMU and other packages.

  ```
  sudo apt-get install qemu uml-utilities virt-manager
  ```

* See [networking notes](networking-qemu-kvm-howto.txt) to setup guest networking.

* Create a virtual HDD image where the OS X operating system will be installed.
  If you change the name of the disk image from `mac_hdd.img` to something
  else, the boot scripts will need updating to point to the new image name. A
  base install of OS X needs 10 GiB of space. Adding Xcode or other large
  software obviously increases that requirement.

  ```
  qemu-img create -f qcow2 mac_hdd.img 64G
  ```

  Now you are ready to install OS X / macOS.

### Installation

To install OS X, you can use the included `boot-macOS.sh` script for a more
solid alternate to the following `virsh` method. Use either the `boot-macOS.sh`
method or the following `virsh` method to install OS X / macOS.

* Edit `macOS-libvirt.xml` file and change file paths for `mac_hdd.qcow2` (HDD), `Install_OS_X_10.11_El_Capitan.iso` (bootable ISO image) and `enoch_rev2839_boot` suitably.

* Create a VM by running the following command
  ```bash
  virsh --connect qemu:///system define macOS-libvirt.xml

  ```

* Start the VM in virt-manager and hit return in the console window.

#### Installer Steps

* After booting, the initial language selection should show up.
![screenshot_01](https://cloud.githubusercontent.com/assets/731252/17645877/5136b1ac-61b2-11e6-8d90-29f5cc11ae01.png)

* After selecting the language, fire-up the Disk Utility ...
![screenshot_02](https://cloud.githubusercontent.com/assets/731252/17645881/513b6918-61b2-11e6-91f2-026d953cbe0b.png)

* ... and initialize the new harddisk. If this step fails and the menu bar
  shows "Language Chooser" then see the Debugging section below.

![screenshot_03](https://cloud.githubusercontent.com/assets/731252/17645878/51373d48-61b2-11e6-8740-69c86bf92d31.png)
![screenshot_04](https://cloud.githubusercontent.com/assets/731252/17645879/513ae704-61b2-11e6-9a54-109c37132783.png)

* After disk initialization, open a terminal window (in the Utilities menu) and recursively copy the /Extra folder
  to the newly initialized target volume using
  ```bash
   cp -av /Extra "/Volumes/NewVolumeName"
  ```
* When done, quit Terminal.
![screenshot_05](https://cloud.githubusercontent.com/assets/731252/17645876/5136ad6a-61b2-11e6-84cd-cb7851119292.png)

* Now, you can continue with the installation as usual
![screenshot_06](https://cloud.githubusercontent.com/assets/731252/17645880/513b2c3c-61b2-11e6-889c-3e4f5a0612ca.png)

* When finished, the VM will reboot automatically and the first time setup continues as usual.
![screenshot_07](https://cloud.githubusercontent.com/assets/731252/17645882/51517a50-61b2-11e6-8bb5-70c810d80b2b.png)

#### Post-Installation Recommendations
* The `boot*.sh` scripts have the installation ISO listed in them but this is
  only required for installation. Once installation is complete, comment out
  the `-device` and `-drive` lines referring to MacDVD and the installation ISO.

* Inside the guest, you may modify the `/Extra/org.chameleon.Boot.plist` file
  to change the default resolution of the virtual screen. See [notes](notes.md)
  for instructions on how to do this and some limitations on the resolution
  choices.

* Download a Chameleon wizard such as Chameleon Wizard or Champlist in order to
  generate a usable smbios.plist. This file goes into `/Extra` and can be used
  to assign a reasonable serial number to your virtual Mac. Generating this file
  sometimes fixes software incompatibilities that occur when the software can't
  determine what Apple hardware it is running on.

* For better mouse behavior, install https://github.com/pmj/QemuUSBTablet-OSX and
  configure QEMU to use the "usb-tablet" absolute pointing device.

* To get sound on your virtual Mac, see the "Virtual Sound Device" in [notes](notes.md).

### Debugging

* For macOS Sierra change the CPU model from `core2duo` to `Penryn`. The
  `boot-macOS.sh` script already has this change.

* While booting from the macOS Sierra ISO installer, you might get stuck on the
  "Language Chooser" menu bar (with no option to launch Disk Utility). The
  solution is to use Ctrl+F2 and arrow keys to navigate the "macOS Installer"
  menu bar, and to launch the "Disk Utility".

  An alternate solution is to type `Super-T` (where `Super` is the Mac
  command/clover key next to the `Alt` key). Type this sequence multiple times
  until a terminal window opens up. In the termianl window type:

  ```
  diskutil list
  ```

  This will generate a list of all attached disks. Look for the disk with a
  size similar to the `mac_hdd.img` created in an earlier step. Once identified,
  note the disk number. Run a command to initialize the filesystem.

  ```
  diskutil eraseDisk JHFS+ <name of disk> <disk#>
  ```

  For example: `diskutil eraseDisk JHFS+ SYS disk2`

  Then select your language and click the forward arrow to move to the next step.

* Host machine may need the following tweak for this to work,

  ```
  echo 1 > /sys/module/kvm/parameters/ignore_msrs
  ```

* Type the following in the bootloader if the guest VM fails to boot (some
  older ISO images may require this),

  ```
  "KernelBooter_kexts"="Yes" "CsrActiveConfig"="103"
  ```

* If you see "hdiutil: attach failed - Resource busy" error message during the
  ISO creation step, quit the "Install macOS Sierra" program and unmount
  (eject) the "Install macOS Sierra" device. Disk Utility can help for
  unmouting disk images.

  ```
  $ hdiutil info
  $ hdiutil detach /dev/disk2  # or something similar
  ```

* If the App Store doesn't work, check the [notes file](notes.md) for instructions on how to solve this.

* If you are getting "Dont_Steal_MacOS" related errors, see `Building QEMU` (recommended option) and
  `FakeSMC installation` sections in [notes file](notes.md).

* If the boot process is getting stuck on the Apple logo, upgrade your host
  kernel and QEMU. For example, Linux 3.16.x from Debian 8 is known to be
  problematic, whereas Linux 4.9.x with QEMU 2.8.x works fine on the same
  distribution.

### References

* https://github.com/Karlson2k/k2k-OSX-Tools

* [Mac OS X 10.11 El Capitan – VM on unRAID](https://macosxvirtualmachinekvm.wordpress.com/guide-mac-os-x-10-11-el-capitan-vm-on-unraid/)

* http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/

* http://forge.voodooprojects.org/p/chameleon/source/changes/HEAD/ (Enoch source)
