### Big Sur - Rough Notes

#### Note: Installation (for the most part) remains the same, except for the retrieval of the DMG file.

- Fetch the `Big Sur` installer using the following command (as usual):

  ```
  ./fetch-macOS.py
  ```

- Unpack the InstallAssistant.pkg

  ```
  $ sudo apt install libarchive-tools #install unzipper for *.pkg
  $ bsdtar xvf InstallAssistant.pkg # extract files
  ```

- Extract `BaseSystem.dmg` from `SharedSupport.dmg`:

  ```
  7z x SharedSupport.dmg  # extract support dmg

  mkdir ~/stuff
  sudo mount -oloop *.hfs ~/stuff
  ```

- There is the required `BaseSystem.dmg` file. To unzip it, first make sure you are in the base directory for `OSX-KVM` and then retrieve the `BaseSystem.dmg` file and convert it to a `BaseSystem.img` file.

  ```
  cd ~/OSX-KVM/

  7z x ~/stuff/com_apple_MobileAsset_MacSoftwareUpdate/*.zip AssetData/Restore/BaseSystem.dmg
  
  sudo umount ~/stuff # .dmg not required any longer

  qemu-img convert AssetData/Restore/BaseSystem.dmg -O raw BaseSystem.img
  ```

- Follow the [main documentation](README.md#installation-preparation) as this point.

- Finally, you can boot `Big Sur` using the following command:

  ```
  ./OpenCore-Boot.sh
  ```
