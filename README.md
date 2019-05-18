### Note

to add q35-speed-patch for libvirt, (4200 and 4920)


# Speedpatch for q35 libvirt to remove slow performance with KVM

svn co -r 4920 svn://svn.code.sf.net/p/cloverefiboot/code Clover


http://s3.nicksherlock.com/forumposts/2016/clover-r4061-qemu-cpu-speed-patch.diff

Download this patch to “edk2/Clover”. Change into that directory and run:

svn patch clover-r4061-qemu-cpu-speed-patch.diff

svn co -r 4920 svn://svn.code.sf.net/p/cloverefiboot/code Clover

Change into the “edk2/Clover” directory, and run:

./ebuild.sh

The default options, which use XCode to build an X64 bootloader, are perfect for us.

After that completes, run “cd CloverPackage; ./makepkg”. This will produce an installable package for us in “edk2/Clover/CloverPackage/sym/Clover_v2.4k_r4920.pkg.”.


# ** FORKED THIS OUT OF IT DRIVING ME TO BRINK of,.q35?

<br>
todo: move q35-dsdt.aml ->
<br>

q35-acpi-dsdt.aml /Volumes/ESP/EFI/CLOVER/ACPI/origin/
<br>


(these qcow2's are built for KVM? q35 model in libvirt)
<br>

(q35-acpi-dsdt.aml appears missing?)
<br>

@q35-acpi-dsdt.aml EFI/CLOVER/ACPI/origin/
<br>

(in the clover image)

This `README` documents the new method to install macOS. The older `README` is
available [here](README-OLD.md).

This new method does *not* require an existing physical/virtual macOS
installation. However, this `new method` requires internet access during the
macOS installation process. This limitation may be addressed in a future
commit.

Note: All blobs and resources included in this repository are re-derivable (all
instructions are included!).

Note: Checkout [ideas.md](ideas.md). This project can always use your help,
time and attention.


### Requirements

* A modern Linux distribution. E.g. Ubuntu 18.04 LTS 64-bit.

* QEMU > 2.11.1

* A CPU with Intel VT-x / AMD SVM support is required

* A CPU with SSE4.1 support is required for macOS Sierra

* A CPU with AVX2 support is required for macOS Mojave

Note: Older AMD CPU(s) are known to be problematic. AMD FX-8350 works but
Phenom II X3 720 does not. Ryzen processors work just fine.


### Installation Preparation

* KVM may need the following tweak on the host machine to work.

  ```
  # echo 1 > /sys/module/kvm/parameters/ignore_msrs
  ```

  To make this change permanent, you may use the following command.

  ```
  $ sudo cp kvm.conf /etc/modprobe.d/kvm.conf
  ```

* Install QEMU and other packages.

  ```
  sudo apt-get install qemu uml-utilities virt-manager dmg2img git wget
  ```

  This step may need to be adapted for your Linux distribution.

* Clone this repository again on your QEMU system. Files from this repository
  are used in the following steps.

  ```
  cd ~

  git clone https://github.com/kholia/OSX-KVM.git

  cd OSX-KVM
  ```

* Fetch macOS installer.

  ```
  ./fetch-macOS.py
  ```

  You can choose your desired macOS version here. After executing this step,
  you should have the `BaseSystem.dmg` file in the current folder.

  Attention: Modern NVIDIA GPUs are supported on HighSierra but not on Mojave
  (yet).

  Next, convert this file into a usable format.

  ```
  dmg2img BaseSystem.dmg BaseSystem.img
  ```

* Create a virtual HDD image where macOS will be installed.  If you change the
  name of the disk image from `mac_hdd.img` to something else, the boot scripts
  will need updating to point to the new image name.

  ```
  qemu-img create -f qcow2 mac_hdd_ng.img 128G
  ```

* Setup quick networking by running the following commands.

  ```
  sudo ip tuntap add dev tap0 mode tap

  sudo ip link set tap0 up promisc on

  sudo brctl addif virbr0 tap0
  ```

* Now you are ready to install macOS 🚀


### Installation

- CLI method (primary). Just run the `boot-macOS-NG.sh` script to start the
  installation proces.

  ```
  ./boot-macOS-NG.sh
  ```

  If you are new to installing macOS, see the [older README](README-OLD.md) for
  help.


- GUI method (alternate - functional but needs further debugging work).

  - Edit `macOS-libvirt-NG.xml` file and change the various file paths (search
    for `CHANGEME` strings in that file). The following command should do the
    trick usually.

    ```
    sed -i "s/CHANGEME/$USER/g" macOS-libvirt-NG.xml
    ```

  - Create a VM by running the following command.

    ```bash
    virsh --connect qemu:///system define macOS-libvirt-NG.xml
    ```

  - Launch `virt-manager`, start the `macOS` virtual machine and install macOS
    as usual.

    Note: You may need to run `sudo ip link delete tap0` command before
    `virt-manager` is able to start the `macOS` VM.

    Note: You may need to remove the following block from `macOS-libvirt-NG.xml`
    and run `virsh --connect ...` again.

    ```
    <disk type='file' device='disk'>
    <driver name='qemu' type='raw' cache='writeback'/>
      <source file='/home/CHANGEME/OSX-KVM/BaseSystem.img'/>
      <target dev='sdc' bus='sata'/>
      <boot order='3'/>
      <address type='drive' controller='0' bus='0' target='0' unit='2'/>
    </disk>
    ```


### Post-Installation

* See [networking notes](networking-qemu-kvm-howto.txt) to setup guest networking.

  I have the following commands present in `/etc/rc.local`.

  ```
  #!/bin/bash

  sudo ip tuntap add dev tap0 mode tap
  sudo ip link set tap0 up promisc on
  sudo brctl addif virbr0 tap0
  ```

  This has been enough for me so far.

* To get sound on your virtual Mac, see the "Virtual Sound Device" in [notes](notes.md).

* To passthrough GPUs and other devices, see [these notes](UEFI/README.md).

* Need a different resolution? Check various notes included in this repository.


### Is This Legal?

The "secret" Apple OSK string is widely available on the Internet. It is also included in a public court document [available here](http://www.rcfp.org/sites/default/files/docs/20120105_202426_apple_sealing.pdf). I am not a lawyer but it seems that Apple's attempt(s) to get the OSK string treated as a trade secret did not work out. Due to these reasons, the OSK string is freely included in this repository.

Gabriel Somlo also has [some thoughts](http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/#sec_4) on the legal aspects involved in running macOS under QEMU/KVM.


### Motivation

My aim is to enable macOS based builds + testing, kernel debugging, reversing
and security tasks in an easy, reproducible manner without needing to invest in
Apple's closed ecosystem (too heavily).

Backstory: I was a (poor) student in Canada once and Apple made [my work on
cracking Apple Keychains](https://github.com/magnumripper/JohnTheRipper/) a lot
harder than it needed to be.


### References

* https://github.com/foxlet/macOS-Simple-KVM

* http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/

* https://www.kraxel.org/blog/2017/09/running-macos-as-guest-in-kvm/
