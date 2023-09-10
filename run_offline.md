### How to run the Installation offline without macOS

- Download the ventura file (InstallAssistant.pkg) from https://mrmacintosh.com/macos-ventura-13-full-installer-database-download-directly-from-apple/(https://mrmacintosh.com/macos-ventura-13-full-installer-database-download-directly-from-apple/)
- Create an iso file `InstallAssistant.iso` with the downloaded InstallAssistant.pkg and `run_offline.sh` in the `scripts/run_offline.sh` files
```
mkisofs -allow-limited-size -l -J -r -iso-level 3 -V InstallAssistant -o <output.iso> <source file or directory>

mkisofs -allow-limited-size -l -J -r -iso-level 3 -V InstallAssistant -o InstallAssistant.iso path/to/InstallAssistant.pkg path/to/OSX-KVM/scripts/run_offline.sh
```
#### or
```
genisoimage -allow-limited-size -l -J -r -iso-level 3 -V InstallAssistant -o <output.iso> <source file or directory>

genisoimage -allow-limited-size -l -J -r -iso-level 3 -V InstallAssistant -o InstallAssistant.iso path/to/InstallAssistant.pkg path/to/OSX-KVM/scripts/run_offline.sh
```
- ***On windows, use poweriso***
- Add the following to your `OpenCore-Boot.sh`

```
-drive id=MacDVD,if=none,file="$REPO_PATH/InstallAssistant.iso",format=raw
-device ide-hd,bus=sata.5,drive=MacDVD
```
- Create your qcow2 file
```
qemu-img create -f qcow2 -o preallocation=off mac_hdd_ng.img 256G
```
- Run `./OpenCore-Boot.sh` from the terminal
- Use the `Disk Utility` tool within the macOS installer to partition, and format the virtual disk attached with name **macOS**
- When completed, close `Disk Utility`
- Go to the Terminal in your virtual machine, Click `Utilities`, select `Terminal`
- Run the cmd `sh /Volumes/InstallAssistant/run_offline.sh`
- Wait for a few minutes for the installation window
