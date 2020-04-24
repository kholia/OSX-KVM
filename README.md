### Note

This `README` documents the `new method` to install macOS. The older `README`
is available [here](README-OLD.md).

This `new method` does *not* require an existing physical/virtual macOS
installation. However, this `new method` requires internet access during the
macOS installation process. This limitation may be addressed in a future
commit.

Note: All blobs and resources included in this repository are re-derivable (all
instructions are included!).


### Contributing Back

This project can always use your help, time and attention. I am looking for
help (pull-requests!) with the following work items:

* Create *full* installation (ISO) image without requiring an existing macOS
  physical/virtual installation.

* An Ansible playbook to automate all-the-things!

* Test `accel=hvf` flag on QEMU + macOS Mojave on MacBook Pro.

* Document (share) how you use this project to build + test open-source
  projects / get your stuff done.

* Document how to use this project for iOS development.

* Document how to use this project for XNU kernel debugging and development.

* Document the process to create and reuse VM snapshots. Instantaneous macOS
  boots would be nice this way.

* Document the process to launch a bunch of headless macOS VMs (build farm).

* Document usage of [munki](https://github.com/munki/munki) to deploy software
  to such a `build farm`.

* Enable SSH support out of the box or more easily.

* Better support + docs for AMD Ryzen.

* Patches to unify the various scripts we have. Robustness improvements.


### Requirements

* A modern Linux distribution. E.g. Ubuntu 18.04 LTS 64-bit or later.

* QEMU > 2.11.1

* A CPU with Intel VT-x / AMD SVM support is required

* A CPU with SSE4.1 support is required for >= macOS Sierra

* A CPU with AVX2 support is required for >= macOS Mojave

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
  sudo apt-get install qemu uml-utilities virt-manager dmg2img git wget libguestfs-tools
  ```

  This step may need to be adapted for your Linux distribution.

* Clone this repository on your QEMU system. Files from this repository are
  used in the following steps.

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

  Sample run:

  ```
  $ ./fetch-macOS.py
  #    ProductID    Version    Build   Post Date  Title
  1    061-26578    10.14.5  18F2059  2019-10-14  macOS Mojave
  2    061-26589    10.14.6   18G103  2019-10-14  macOS Mojave
  3    041-91758    10.13.6    17G66  2019-10-19  macOS High Sierra
  4    041-88800    10.14.4  18E2034  2019-10-23  macOS Mojave
  5    041-90855    10.13.5   17F66a  2019-10-23  Install macOS High Sierra Beta
  6    061-44345    10.15.2   19C39d  2019-11-15  macOS Catalina Beta
  7    061-77704    10.15.4  19E242d  2020-02-26  macOS Catalina Beta
  8    061-86291    10.15.3  19D2064  2020-03-23  macOS Catalina
  9    061-96006    10.15.4   19E287  2020-04-08  macOS Catalina

  Choose a product to download (1-9): 9
  ```

  Attention: Modern NVIDIA GPUs are supported on HighSierra but not on later
  versions (yet).

  Next, convert this file into a usable format.

  ```
  dmg2img BaseSystem.dmg BaseSystem.img
  ```

  Note: You can also use the following command to do this conversion, if your
  QEMU version is >= 4.0.0.

  ```
  qemu-img convert BaseSystem.dmg -O raw BaseSystem.img
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
  sudo ip link set dev virbr0 up
  sudo ip link set dev tap0 master virbr0
  ```

  Note: If `virbr0` network interface is not present on your system, it may
  have been deactivated. Try enabling it by using the following commands,

  ```
  virsh net-start default

  virsh net-autostart default
  ```

* Now you are ready to install macOS 🚀


### Installation

- CLI method (primary). Just run the `boot-macOS-Catalina.sh` script to start the
  installation proces.

  ```
  ./boot-macOS-Catalina.sh
  ```

  Experimental: Use the `OpenCore-Boot.sh` script to maximize fun ;)

  If you are new to installing macOS, see the [older README](README-OLD.md) for
  help.

- You are all set! 🙌

- (OPTIONAL) Use this macOS VM disk with libvirt (virt-manager / virsh stuff).

  - Edit `macOS-libvirt-Catalina.xml` file and change the various file paths (search
    for `CHANGEME` strings in that file). The following command should do the
    trick usually.

    ```
    sed -i "s/CHANGEME/$USER/g" macOS-libvirt-Catalina.xml

    virt-xml-validate macOS-libvirt-Catalina.xml
    ```

  - Create a VM by running the following command.

    ```bash
    virsh --connect qemu:///system define macOS-libvirt-Catalina.xml
    ```

  - Launch `virt-manager` and start the `macOS` virtual machine.

    Note: You may need to run `sudo ip link delete tap0` command before
    `virt-manager` is able to start the `macOS` VM.


### Post-Installation

* See [networking notes](networking-qemu-kvm-howto.txt) to setup guest networking.

  I have the following commands present in `/etc/rc.local`.

  ```
  #!/usr/bin/env bash

  sudo ip tuntap add dev tap0 mode tap
  sudo ip link set tap0 up promisc on
  sudo ip link set dev virbr0 up
  sudo ip link set dev tap0 master virbr0
  ```

  This has been enough for me so far.

* To get sound on your virtual Mac, see the "Virtual Sound Device" in [notes](notes.md).

* To passthrough GPUs and other devices, see [these notes](notes.md).

* Need a different resolution? Check out the [notes](notes.md) included in this
  repository.


### Is This Legal?

The "secret" Apple OSK string is widely available on the Internet. It is also included in a public court document [available here](http://www.rcfp.org/sites/default/files/docs/20120105_202426_apple_sealing.pdf). I am not a lawyer but it seems that Apple's attempt(s) to get the OSK string treated as a trade secret did not work out. Due to these reasons, the OSK string is freely included in this repository.

Gabriel Somlo also has [some thoughts](http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/) on the legal aspects involved in running macOS under QEMU/KVM.


### Motivation

My aim is to enable macOS based builds + testing, kernel debugging, reversing
and security tasks in an easy, reproducible manner without needing to invest in
Apple's closed ecosystem (too heavily).

Backstory: I was a (poor) student in Canada once and Apple made [my work on
cracking Apple Keychains](https://github.com/magnumripper/JohnTheRipper/) a lot
harder than it needed to be.
