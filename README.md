Host
----

Ubuntu 15.10 running on i5-6500 CPU.

Fedora 24 running on i5-6500 CPU.

Tested with QEMU 2.4.1 and QEMU 2.5.

ISO Creation
------------

* Run the ISO creation script, making sure to use 'sudo' if possible.

* Copy the ISO from your Mac to your KVM machine.

Enoch Bootloader
----------------

* Download Enoch bootloader from http://www.insanelymac.com/forum/ (requires
  registration).

* Using Pacifist open the “Enoch-rev.####.pkg” file and extract the file called
  "boot" from Core.pkg/usr/standalone/i386/boot

* Rename boot to enoch_rev####_boot.

Installation
------------

```bash
virsh --connect qemu:///system define osx-libvirt-install.xml

```

* Redefine HDD/DVD sources in virt-manager

* Start the VM in virt-manager and hit return in the console window.

* After booting, The initial language selection should show up.
![screenshot_01](https://cloud.githubusercontent.com/assets/731252/17645877/5136b1ac-61b2-11e6-8d90-29f5cc11ae01.png)

* After selecting the language, fire-up the Disk Utility ...
![screenshot_02(https://cloud.githubusercontent.com/assets/731252/17645881/513b6918-61b2-11e6-91f2-026d953cbe0b.png)

* ... and nitialize the new harddisk.
![screenshot_03](https://cloud.githubusercontent.com/assets/731252/17645878/51373d48-61b2-11e6-8740-69c86bf92d31.png)
![screenshot_04](https://cloud.githubusercontent.com/assets/731252/17645879/513ae704-61b2-11e6-9a54-109c37132783.png)

* After disk initialization, open a terminal window (in the Utilities menu) and recursively copy the /Extra folder
  to the newly initialized target volume using cp -av /Extra "/Volumes/NewVolumeName" 
![screenshot_05](https://cloud.githubusercontent.com/assets/731252/17645876/5136ad6a-61b2-11e6-84cd-cb7851119292.png)

* Now, you can continue with the installation as usual
![screenshot_06](https://cloud.githubusercontent.com/assets/731252/17645880/513b2c3c-61b2-11e6-889c-3e4f5a0612ca.png)

* When finished, the VM will reboot automatically and the first time setup continues as usual.
![screenshot_07](https://cloud.githubusercontent.com/assets/731252/17645882/51517a50-61b2-11e6-8bb5-70c810d80b2b.png)



References
----------

* https://github.com/Karlson2k/k2k-OSX-Tools

* https://macosxvirtualmachinekvm.wordpress.com/guide-mac-os-x-10-11-el-capitan-vm-on-unraid/

* http://www.contrib.andrew.cmu.edu/~somlo/OSXKVM/

* http://bit.do/bootable
