### Introduction
The Clover bootloader is installed directly onto the EFI partition held within the CloverNG.qcow2 file.
In order to access the files within the image and modify the boot config, we first need to convert the image.

### Requirements
* [qemu-img](https://www.qemu.org/download/) 
* A text editor (Nano, Vim, emacs, etc) 
* Linux distribution (Ubuntu 19.04 was used in this case) 
* Clover bootloader or MacOS (to get the UUID of the target drive) 
* Math skills (Just one simple multiplication problem) 

### Steps
* Start by booting up your MacOS image with the provided BootMacOSCatalina.sh script in the root of the repo

* Once you reach the Clover boot menu, navigate to the drive with MacOS installed and press the SPACE bar
  From there you'll see the drive's UUID; please save this as you will need it later

* Navigate to the folder containing the existing CloverNG.qcow2 image
  Convert the qcow2 image into a raw disk image
  ```
  qemu-img -f qcow2 -O raw CloverNG.qcow2 CloverNG.raw
  ```

* Determine the starting offset of the EFI parition on the disk
  ```
  fdisk -l CloverNG.raw
  ``` 
  Your output would likely be this:
  ```
  Disk CloverNG.raw: 256 MiB, 268435456 bytes, 524288 sectors
  Units: sectors of 1 * 512 = 512 bytes
  Sector size (logical/physical): 512 bytes / 512 bytes
  I/O size (minimum/optimal): 512 bytes / 512 bytes
  Disklabel type: gpt
  Disk identifier: 59003A91-A770-42D7-8709-A7F45743ABD8

  Device         Start    End Sectors   Size Type
  CloverNG.raw1   2048 200000  197953  96.7M EFI System
  CloverNG.raw2 202048 522240  320193 156.4M Linux filesystem
  ```
  Here we see that the EFI partition starts at 2048.
  To calcuate the offset, we multiply the starting index by the sector size:
  ```
  >>> 2048*512
  1048576
  ```  

* Mount the EFI partition from the raw disk image using the offset we just calculated
  ```
  sudo mkdir /mnt/img
  sudo mount -t vfat -oloop,offest=1048576 CloverNG.raw /mnt/img
  ``` 

* Edit the config inside of the EFI partition
  ```
  nano /mnt/img/EFI/CLOVER/config.plist
  ```
  Change the "Timeout" value to 0 (default=5)
  Change the "DefaultVolume" value to the UUID of the target drive (see above)
  Feel free to change any other settings if you know what's going on

* Unmount the raw image's EFI partition
  ```
  sudo umount /mnt/img
  ```

* Convert the raw image back into a qcow2 file
  ```
  qemu-img -f raw -O qcow2 CloverNG.raw CloverCata.qcow2
  ```

* Try booting with this new volume using QEMU

### Notes
* Available boot options for clover [here](https://sourceforge.net/p/cloverefiboot/wiki/Configuration/)
* Explanation on raw disk offsets [here](https://major.io/2010/12/14/mounting-a-raw-partition-file-made-with-dd-or-dd_rescue-in-linux/)
* In KVM, both the Clover volume and the MacOS Volume must be selected as boot volumes in the Virtual Machine's options for proper drive discovery
