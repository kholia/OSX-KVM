### Note

This `README.md` documents the process of creating a `Virtual Hackintosh`
system.

Note: All blobs and resources included in this repository are re-derivable (all
instructions are included!).

:green_heart: Looking for **commercial** support with this stuff? I am [available
over email](mailto:dhiru.kholia@gmail.com?subject=[GitHub]%20OSX-KVM%20Commercial%20Support%20Request&body=Hi%20-%20We%20are%20interested%20in%20purchasing%20commercial%20support%20options%20for%20your%20project.) for a chat for **commercial support options only**.

Looking for `Big Sur` support? See these [notes](Big-Sur.md).

Yes, we support offline macOS installations now 🎉


### Contributing Back

This project can always use your help, time and attention. I am looking for
help (pull-requests!) with the following work items:

* Create *full* installation (ISO) image without requiring an existing macOS
  physical/virtual installation.

* Documentation around running macOS on popular cloud providers (GCP, AWS). See
  the `Is This Legal?` section and associated references.

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

* A modern Linux distribution. E.g. Ubuntu 20.04 LTS 64-bit or later.

* QEMU >= 4.2.0

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
  sudo apt-get install qemu uml-utilities virt-manager git wget libguestfs-tools -y
  ```

  This step may need to be adapted for your Linux distribution.

* Clone this repository on your QEMU system. Files from this repository are
  used in the following steps.

  ```
  cd ~

  git clone --depth 1 https://github.com/kholia/OSX-KVM.git

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
   #    ProductID    Version   Post Date  Title
   1    061-26578    10.14.5  2019-10-14  macOS Mojave
   2    061-26589    10.14.6  2019-10-14  macOS Mojave
   3    041-91758    10.13.6  2019-10-19  macOS High Sierra
   4    041-88800    10.14.4  2019-10-23  macOS Mojave
   5    041-90855    10.13.5  2019-10-23  Install macOS High Sierra Beta
   6    061-86291    10.15.3  2020-03-23  macOS Catalina
   7    001-04366    10.15.4  2020-05-04  macOS Catalina
   8    001-15219    10.15.5  2020-06-15  macOS Catalina
   9    001-36735    10.15.6  2020-08-06  macOS Catalina
  10    001-36801    10.15.6  2020-08-12  macOS Catalina
  11    001-51042    10.15.7  2020-09-24  macOS Catalina

  Choose a product to download (1-11): 11
  ```

  Attention: Modern NVIDIA GPUs are supported on HighSierra but not on later
  versions (yet).

  Next, convert this file into a usable format.

  ```
  qemu-img convert BaseSystem.dmg -O raw BaseSystem.img
  ```

* Create a virtual HDD image where macOS will be installed. If you change the
  name of the disk image from `mac_hdd.img` to something else, the boot scripts
  will need to be updated to point to the new image name.

  ```
  qemu-img create -f qcow2 mac_hdd_ng.img 128G
  ```

  NOTE: Create this HDD image file on a fast SSD/NVMe disk for best results.

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

- CLI method (primary). Just run the `OpenCore-Boot.sh` script to start the
  installation proces.

  ```
  ./OpenCore-Boot.sh
  ```

  Note: This same script works for Big Sur, Catalina, Mojave, and High Sierra.

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


### Setting Expectations Right

Nice job on setting up a `Virtual Hackintosh` system! Such a system can be used
for a variety of purposes (e.g. software builds, testing, reversing work), and
it may be all you need, along with some tweaks documented in this repository.

However, such a system lacks graphical acceleration, a reliable sound sub-system,
USB (3) functionality and other similar things. To enable these things, take a
look at our [notes](notes.md). We would like to resume our testing and
documentation work around this area. Please [reach out to us](mailto:dhiru.kholia@gmail.com?subject=[GitHub]%20OSX-KVM%20Funding%20Support)
if you are able to fund this area of work.

It is possible to have 'beyond-native-apple-hw' performance but it does require
work, patience, and a bit of luck (perhaps?).


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

  Note: You may need to [enable the `rc.local` functionality manually on modern Ubuntu versions](https://linuxmedium.com/how-to-enable-etc-rc-local-with-systemd-on-ubuntu-20-04/).

* To get sound on your virtual Mac, see the "Virtual Sound Device" in [notes](notes.md).

* To passthrough GPUs and other devices, see [these notes](notes.md).

* Need a different resolution? Check out the [notes](notes.md) included in this repository.

* To generate your own SMBIOS, use [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS).


### Is This Legal?

The "secret" Apple OSK string is widely available on the Internet. It is also included in a public court document [available here](http://www.rcfp.org/sites/default/files/docs/20120105_202426_apple_sealing.pdf). I am not a lawyer but it seems that Apple's attempt(s) to get the OSK string treated as a trade secret did not work out. Due to these reasons, the OSK string is freely included in this repository.

Gabriel Somlo also has [some thoughts](http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/) on the legal aspects involved in running macOS under QEMU/KVM.


### Motivation

My aim is to enable macOS based educational tasks, builds + testing, kernel
debugging, reversing, and macOS security research in an easy, reproducible
manner without needing to invest in Apple's closed ecosystem (too heavily).

These `Virtual Hackintosh` systems are not intended to replace the genuine
physical macOS systems.

Backstory: I was a (poor) student in Canada once and Apple made [my work on cracking Apple Keychains](https://github.com/openwall/john/blob/bleeding-jumbo/src/keychain_fmt_plug.c) a lot harder than it needed to be.
