### Big Sur - Rough Notes

#### Note: Installation (for the most part) remains the same, except for the retrieval of the DMG file.

- Fetch the `Big Sur` installer using the following command (as usual):

  ```
  ./fetch-macOS.py
  ```

- Get `xar` software.

  ```
  cd ~  # modify as needed

  git clone https://github.com/VantaInc/xar.git

  cd xar/xar

  ./autogen.sh

  make
  ```

- Install dependencies for `darling-dmg`. (The following is for Debian/Ubuntu, different distros name packages differently.)

  ```
  apt install libxml2-dev libbz2-dev libfuse-dev cmake build-essential
  ```

- Get `darling-dmg` software.

  ```
  cd ~  # modify as needed

  git clone https://github.com/darlinghq/darling-dmg.git

  cd darling-dmg

  # Install required deps - RTFM please ;)

  cmake .

  make
  ```

- Extract `SharedSupport.dmg` from the downloaded `InstallAssistant.pkg` file (around 9 GB).

  ```
  $ ~/xar/xar/src/xar -tf InstallAssistant.pkg  # list files
  Bom
  Payload
  Scripts
  PackageInfo
  SharedSupport.dmg
  ```

  ```
  $ ~/xar/xar/src/xar -xf InstallAssistant.pkg  # extract files
  ```

- Extract `BaseSystem.dmg` from `SharedSupport.dmg`:

  ```
  7z l SharedSupport.dmg  # This will list the files in the archive

  mkdir ~/stuff
  ~/darling-dmg/darling-dmg SharedSupport.dmg ~/stuff  # Mounts SharedSupport.dmg to ~/stuff

  $ 7z l ~/stuff/com_apple_MobileAsset_MacSoftwareUpdate/ee3ab6c04234b360dd8fca93c0ae49f957bf0843.zip  # The string of letters and numbers will vary
  ...
  2020-11-06 18:57:48 .....    652236311    646767350  AssetData/Restore/BaseSystem.dmg
  ```

- There is the required `BaseSystem.dmg` file. To unzip it, first make sure you are in the base directory for `OSX-KVM` and then retrieve the `BaseSystem.dmg` file and convert it to a `BaseSystem.img` file.

  ```
  cd ~/OSX-KVM/

  7z x ~/stuff/com_apple_MobileAsset_MacSoftwareUpdate/ee3ab6c04234b360dd8fca93c0ae49f957bf0843.zip AssetData/Restore/BaseSystem.dmg

  mv AssetData/Restore/BaseSystem.dmg .

  qemu-img convert BaseSystem.dmg -O raw BaseSystem.img
  ```

- Follow the [main documentation](README.md#installation-preparation) as this point.

- Finally, you can boot `Big Sur` using the following command:

  ```
  ./OpenCore-Boot.sh
  ```
