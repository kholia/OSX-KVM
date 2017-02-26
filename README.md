### Host System Details

Known to work on:

* Ubuntu 15.10 running on i5-6500 CPU.

* Ubuntu 16.10 running on i7-3960X CPU.

* Fedora 24 running on i5-6500 + i7-6600U CPU.

Tested with QEMU 2.4.1, 2.5, and 2.6.1.

AMD CPU(s) are known to be problematic. AMD FX-8350 works but Phenom II X3 720
does not.

Intel VT-x / AMD SVM is required.

### Installation Preparation

#### Prep On Your Current OSX
* Download OS X El Capitan or macOS Sierra installer from Apple App Store. Installer is usually saved to the `/Applications` path.

* Clone this repository. Files included in this repository are needed for ISO
  creation.

  ```
  git clone https://github.com/kholia/OSX-KVM.git
  ```

* Run the ISO creation script `create_install_iso.sh` included in this
  repository. Run it with `sudo`.

  This script supports specifying the path to OS X / macOS installation
  application manually via the `-a` option.

  The script builds an installer ISO and includes a directory called `/Extras`
  which will contain the `org.chameleon.boot.plist` file.

  ```
  sudo ./create_install_iso.sh -a /path/to/Install_macOS_Sierra_(OS_X_10.12.3).iso	\
  -i /path/to/output/installer.iso
  ```

  See Debugging section for help if this step has problems.

* Save the final ISO to copy from your Mac to your QEMU/KVM machine.

#### Prep On Your QEMU System
  * Install qemu.
  ```
  sudo apt-get install qemu
  ```

  * Install packages to support virtual management and OSX networking.
  ```
  sudo apt-get install uml-utilities virt-manager
  sudo ip tuntap add dev tap0 mode tap
  sudo ip link set tap0 up promisc on
  sudo brctl addif virbr0 tap0
  ```

  * Create directories for storing your virtual machines. Pick your own structure but here's an example.
  ```
  mkdir -p $HOME/virtual_machines/osx
  ```

  * Copy the ISO from your Mac to this machine.
  ```
  scp -p <IP of Mac>:path/to/ISO/Installer.iso $HOME/virtual_machines/osx
  ```

  * Clone this repository again for the rest of the support files.
  ```
  cd $HOME/virtual_machines/osx
  git clone https://github.com/kholia/OSX-KVM.git
  ```

* Create a virtual HDD image where the OSX operating system will be installed. If you change the name of the disk image from `mac_hdd.img` to something else, the boot scripts will need updating to point to the new image name. A base install of OSX needs 10G of space. Adding XCode or other large software obviously increases that requirement.
  ```bash
   qemu-img create -f qcow2 mac_hdd.img 64G
  ```

  Now you are ready to install OSX.

### Installation

There are two recommended ways to boot the installation ISO.

#### Boot Method 1

  * Copy some files from the git repository directory to the virtual machine directory to suppor the installation.
  ```
  cd $HOME/virtual_machines/osx/OSX-KVM
  cp boot-macOS.sh ..
  cp enoch_rev2848_boot ..
  ```

  * We will use the `boot-macOS.sh` script for booting a macOS Sierra (OSX 10.12.x) system. The `boot.sh` script is for booting an El Capitan (10.11.x) system.

  * Run the boot script with `sudo`. To run without sudo, check the qemu documentation for assistance.
  ```
  sudo ./boot-macOS.sh
  ```

  Jump to Installer Steps next.

#### Boot Method 2

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

* ... and initialize the new harddisk. If this step fails and the menubar shows "LanguageChooser" then go to the Debugging section and resolve the issue with one of the solutions listed there.
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
* The `boot*.sh` scripts have the installation ISO listed in them but this is only required for installation. Once installation is complete, comment out the `-device` and `-drive` lines referring to MacDVD and the installation ISO.

* Inside the guest, you may modify the `/Extras/org.chameleon.boot.plist` file to change the default resolution of the virtual screen. See [notes](notes.md) for instructions on how to do this and some limitations on the resolution choices.

* If the App Store doesn't work, check the [notes file](notes.md) for instructions on how to solve this.

* Download a Chameleon wizard such as Chameleon Wizard or Champlist in order to generate a usable SMBios.plist. This file goes into `/Extras` and can be used to assign a reasonable serial number to your virtual Mac. Generating this file sometimes fixes software incompatibilities that occur when the software can't determine what Apple hardware it is running on.

### Debugging

* For macOS Sierra change the CPU model from `core2duo` to `Penryn`. The
  `boot-macOS.sh` script already has this change.

* While booting from the macOS Sierra ISO installer, you might get stuck on the
  "Language Chooser" menu bar (with no option to launch Disk Utility). The
  solution is to type `super-T` (where "super" is the Mac command/clover key next to the `alt` key). Type this sequence multiple times until a terminal window opens up. In the window type:
  ```
  diskutil list
  ```
  This will generate a list of all attached disks. Look for the disk with a size similar to the `mac_hdd.img` created in an earlier step. Once identified, note the disk number. Run a command to initialize the filesystem.
  ```
  diskutil eraseDisk JHFS+ <name of disk> <disk#>
    ```
  For example: `diskutil eraseDisk JHFS+ MyKVMacHD disk2`

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

### Credits

* Meissa - better networking documentation

* PJ Meyer (pjmeyer) - compatibility with modern versions of GNU mktemp

* Robert DeRose (RobertDeRose) and Dirk Bajohr (isolution-de) - macOS support

* Fritz Elfert (felfert) - cleanups, better documentation, and nicer ISO creation script

* Ian McDowell (IMcD23) - more documentation, and better ISO creation script

* voobscout - libvirt XML file

* Evgeny Grin (Karlson2k) - for the original ISO creation script

* Gabriel L. Somlo - for getting things started

* http://www.insanelymac.com/ - Enoch bootloader

### References

* https://github.com/Karlson2k/k2k-OSX-Tools

* [Mac OS X 10.11 El Capitan – VM on unRAID](https://macosxvirtualmachinekvm.wordpress.com/guide-mac-os-x-10-11-el-capitan-vm-on-unraid/)

* http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/
