### Notes

* Enoch bootloader is not used for macOS High Sierra. Clover is used instead.


### Host System Details

Known to work on:

* Fedora 25 running on i7-6600U CPU.

* Ubuntu 17.04 running on i5-6500 CPU.

Tested with QEMU >= 2.9.1 and Linux 4.12.x. A CPU with SSE4.1 support is
required for macOS High Sierra. Intel VT-x / AMD SVM is required.


### Installation Preparation

#### Preparation steps on your current macOS installation

* Download macOS High Sierra installer from Apple App Store.

* Clone this repository. Files included in this repository are needed for ISO
  creation.

  ```
  git clone https://github.com/kholia/OSX-KVM.git
  ```

* Run the ISO creation script `create_iso_highsierra.sh` included in this
  folder. Run it with `sudo`.

* Copy the generated ISO image from your Mac's Desktop to your QEMU/KVM machine.

#### Preparation steps on your QEMU system

* Clone this repository again on your QEMU system. Files from this repository are used in the following steps.

* Install QEMU and other packages.

  ```
  sudo apt-get install qemu uml-utilities virt-manager libguestfs-tools
  ```

* See [networking notes](../networking-qemu-kvm-howto.txt) to setup guest networking.

* Create a virtual HDD image where macOS will be installed.

  ```
  qemu-img create -f qcow2 mac_hdd.img 128G
  ```

  Now you are ready to macOS High Sierra.

* Create bootable Clover disk.


  ```
  sudo ./clover-image.sh --iso Clover-v2.4k-4220-X64.iso --cfg clover/config.plist.stripped.qemu --img Clover.qcow2
  ```

  Instead of building your own bootable Clover disk, you may use the included `Clover.qcow2` disk image.


### Installation

To install macOS High Sierra, use the included `boot-macOS-HS.sh` script.

Note: Set the OVMF resolution to 1024x768. This can be done via the OVMF menu,
which you can reach with a press of the ESC button during the OVMF boot logo.
In the OVMF menu settings, set Device Manager -> OVMF Platform Configuration ->
Change Preferred Resolution for Next Boot to 1024x768 . Commit changes and exit
the OVMF settings. Relaunch the `boot-macOS-HS.sh` script.

#### Installer Steps

* After booting, the initial language selection should show up.

* After selecting the language, fire-up the Terminal program and prepare the
  hard drive for installation.

  ```
  diskutil list
  diskutil eraseDisk JHFS+ macOS disk0  # adapt this according to your system
  ```

* When done, quit Terminal.

* Now, you can continue with the installation as usual.

* When finished, the VM will reboot automatically and the first time setup continues as usual.

#### Post-Installation Recommendations

* Install Clover to the main hard drive where macOS High Sierra was installed
  in previous steps. See [UEFI notes](../UEFI/README.md) for details.

* For debugging and general tips, see the main [README.md](../README.md) file
  and [notes.md](../notes.md) file.

### Credits

* Nicholas Sherlock (http://www.nicksherlock.com)

* https://www.kraxel.org/blog/2017/09/running-macos-as-guest-in-kvm/

* https://sourceforge.net/projects/cloverefiboot/files/Bootable_ISO/
