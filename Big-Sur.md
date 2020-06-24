### Big Sur - Rough Notes

- Fetch the `Big Sur` installer using the following command:

  ```
  ./fetch-macOS.py --big-sur
  ```

- Get `xar` software.

  ```
  cd ~  # modify as needed

  git clone https://github.com/VantaInc/xar.git

  cd xar/xar

  ./autogen.sh

  make
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

- Extract `BaseSystem.dmg` from the downloaded `InstallAssistant.pkg` file (around 9 GB).

  ```
  $ ~/xar/xar/src/xar -tf InstallAssistant.pkg
  Bom
  Payload
  Scripts
  PackageInfo
  SharedSupport.dmg
  ```

  Extract `BaseSystem.dmg` from `SharedSupport.dmg`:

  ```
  ~/xar/xar/src/xar -xf InstallAssistant.pkg

  7z l SharedSupport.dmg   # test ok

  mkdir stuff
  darling-dmg SharedSupport.dmg ~/stuff

  $ 7z l ~/stuff/com_apple_MobileAsset_MacSoftwareUpdate/0dc2cd535db0da2a9f559215671686ea4c055394.zip
  ...
  2020-06-18 01:39:16 D....            0            0  AssetData/Restore
  2020-06-18 01:38:34 .....         2848         2729  AssetData/Restore/BaseSystem.chunklist
  2020-06-18 01:39:18 .....    740415556    735058236  AssetData/Restore/BaseSystem.dmg
  ```

  There is the required `BaseSystem.dmg` file.

- Boot `Big Sur` using the following command:

  ```
  ./OpenCore-BS.sh
  ```
