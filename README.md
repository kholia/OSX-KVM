### Host System Details

Ubuntu 15.10 running on i5-6500 CPU.

Fedora 24 running on i5-6500 + i7-6600U CPU.

Tested with QEMU 2.4.1 and QEMU 2.5.

AMD CPU(s) are known to be problematic. AMD FX-8350 works but Phenom II X3 720
does not.

Intel VT-x / AMD SVM is required.

### ISO Creation

* Download OS X El Capitan or macOS Sierra installer from Apple App Store.

* Clone this repository. Files included in this repository are needed for ISO
  creation.

  ```
  git clone https://github.com/kholia/OSX-KVM.git
  ```

* Run the ISO creation script `create_install_iso.sh` included in this
  repository, making sure to use 'sudo'.

  This script supports specifying the path to OS X / macOS installation
  application manually via the `-a` option.

* Copy the ISO from your Mac to your QEMU/KVM machine.

### Installation

See `boot.sh` / `boot-macOS.sh` file for a more solid alternate to the
following virsh method.

* Create a virtual HDD image where the operating system will be installed.
  ```bash
   qemu-img create -f qcow2 mac_hdd.img 64G
  ```

* Edit `macOS-libvirt.xml` file and change file paths for `mac_hdd.qcow2` (HDD), `Install_OS_X_10.11_El_Capitan.iso` (bootable ISO image) and `enoch_rev2839_boot` suitably.

* Create a VM by running the following command
  ```bash
  virsh --connect qemu:///system define macOS-libvirt.xml

  ```

* Start the VM in virt-manager and hit return in the console window.

* After booting, the initial language selection should show up.
![screenshot_01](https://cloud.githubusercontent.com/assets/731252/17645877/5136b1ac-61b2-11e6-8d90-29f5cc11ae01.png)

* After selecting the language, fire-up the Disk Utility ...
![screenshot_02](https://cloud.githubusercontent.com/assets/731252/17645881/513b6918-61b2-11e6-91f2-026d953cbe0b.png)

* ... and initialize the new harddisk.
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

### Debugging

* For macOS Sierra change the CPU model from `core2duo` to `Penryn`. The
  `boot-macOS.sh` script already has this change.

* While booting from the macOS Sierra ISO installer, you might get stuck on the
  "Language Chooser" menu bar (with no option to launch Disk Utility). The
  solution is to wait for a few seconds on the "Language Chooser" screen itself
  without pressing the forward button.

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
