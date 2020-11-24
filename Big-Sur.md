# Big Sur Installation

Note: Installation (for the most part) remains the same, except for the retrieval of the DMG file.

# Install Dependencies

## Fedora
`sudo dnf install p7zip p7zip-plugins qemu git wget libguestfs-tools`

Download and install: https://src.fedoraproject.org/rpms/uml_utilities

## Ubuntu
`sudo apt-get install qemu uml-utilities virt-manager git wget libguestfs-tools p7zip-full -y`

# Creating Installation Media and Disk Image
Open terminal and copy and paste the following code blocks below each step.
* Clone and navigate into OSX-KVM repository, make a placeholder for mounting HFS 
  * `git clone https://github.com/kholia/OSX-KVM.git`
  * `cd OSX-KVM && mkdir tmp`
* Select macOS version Big Sur and download
  * `./fetch-macOS.py` 
* Extract and mount filesystem to `tmp`
  * `7z e -txar InstallAssistant.pkg '*.dmg'`
  * `7z e -tdmg SharedSupport.dmg 5.hfs`
  * `sudo mount -oloop *.hfs tmp`
* Extract BaseSystem.dmg and convert it to .img
  * `7z l tmp/com_apple_MobileAsset_MacSoftwareUpdate/*.zip`
  * `7z e tmp/*MacSoftwareUpdate/*.zip AssetData/Restore/Base*.dmg`
  * `qemu-img convert BaseSystem.dmg -O raw BaseSystem.img`
* Create Disk Image and Unmount (currently set at 120GB)
  * `qemu-img create -f qcow2 mac_hdd_ng.img 120G`
  * `sudo umount tmp`

Finally, you can boot `Big Sur` using the following command:

  ```
  ./OpenCore-Boot.sh
  ```
  
Follow the [main documentation](README.md#installation-preparation) for more information.
