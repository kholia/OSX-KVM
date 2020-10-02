### Description

This document helps with setting up a virtual macOS system.


### Notes

- Generate macOS Mojave / Catalina installation ISO.

  This step currently needs to run on an existing macOS system.

  ```
  cd ~/OSX-KVM/Mojave

  ./create_iso_mojave_ng.sh
  ```


### Tweaks for macOS

1. Disable `Energy Saver` in `System Preferences`.

2. Disable `Screen Saver` in `System Preferences -> Desktop & Screen Saver`.

3. Turn off indexing using the following command.

   ```
   sudo mdutil -a -i off
   ```

4. Enable `Remote Login` (aka SSH) via `System Preferences -> Sharing`.


### Debugging Tips

- Get `savevm` to work:

  ```
  (qemu) savevm
  Error while writing VM state: No space left on device
  ```

  Ensure that you have plenty of free space in `/var/tmp` and `/`.


  To use a separate storage location for storing snapshots, use the following
  trick (from `zimbatm`):

  ```
  export TMPDIR=$PWD/tmp
  ``

- Fix weird boot problems:

  ```
  cp OVMF_VARS-1024x768.fd.bak OVMF_VARS-1024x768.fd
  ```
