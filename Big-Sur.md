### Big Sur - Rough Notes

#### Note: Installation (for the most part) remains the same, except for the retrieval of the DMG file.

- Fetch the `Big Sur` installer using the following command (as usual):

  ```
  ./fetch-macOS.py
  ```

- Unpack the download InstallAssistant.pkg file:

  ```
  7z e -txar InstallAssistant.pkg *.dmg  # extract files
  ```

  At the end of this step, we get the `SharedSupport.dmg` file.

- Extract `BaseSystem.dmg` from this `SharedSupport.dmg` file:

  ```
  7z e -tdmg SharedSupport.dmg 5.hfs  # extract support dmg

  mkdir ~/stuff
  sudo mount -oloop *.hfs ~/stuff  # mount the hfs filesystem

  7z l ~/stuff/com_apple_MobileAsset_MacSoftwareUpdate/*.zip  # list files from this zip file
  ...
  2020-11-06 18:57:48 .....    652236311    646767350  AssetData/Restore/BaseSystem.md
  ```

  There is the required `BaseSystem.dmg` file. To unzip it, first make sure you
  are in the base directory for `OSX-KVM` and then extract the `BaseSystem.dmg`
  file.

  ```
  cd ~/OSX-KVM/

  7z e ~/stuff/*MacSoftwareUpdate/ *.zip AssetData/Restore/Base*.dmg

  sudo umount ~/stuff
  ```

* Convert this extracted `BaseSystem.dmg` file into the `BaseSystem.img` file.

  ```
  qemu-img convert BaseSystem.dmg -O raw BaseSystem.img
  ```

- Follow the [main documentation](README.md#installation-preparation) as this point.

- Finally, you can boot `Big Sur` using the following command:

  ```
  ./OpenCore-Boot.sh
  ```
