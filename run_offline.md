### How to run the Installation offline without macOS

* Download the Ventura installer (`InstallAssistant.pkg`) from [https://mrmacintosh.com/macos-ventura-13-full-installer-database-download-directly-from-apple/](https://mrmacintosh.com/macos-ventura-13-full-installer-database-download-directly-from-apple/)

* Create an ISO file `InstallAssistant.iso` with the `InstallAssistant.pkg` and
  `scripts/run_offline.sh` files.

  ```
  mkisofs -allow-limited-size -l -J -r -iso-level 3 -V InstallAssistant -o InstallAssistant.iso path/to/InstallAssistant.pkg scripts/run_offline.sh
  ```

* Add the following to your `OpenCore-Boot.sh`

  ```
  -drive id=MacDVD,if=none,file="$REPO_PATH/InstallAssistant.iso",format=raw
  -device ide-hd,bus=sata.5,drive=MacDVD
  ```

* Run `./OpenCore-Boot.sh` from the terminal

* Use the `Disk Utility` tool within the macOS installer to partition, and
  format the virtual disk attached with name **macOS**

* When completed, close `Disk Utility`

* Go to the Terminal in your virtual machine, Click `Utilities`, select `Terminal`

* Run the `sh /Volumes/InstallAssistant/run_offline.sh` command

* Wait for a few minutes for the installation window to appear
