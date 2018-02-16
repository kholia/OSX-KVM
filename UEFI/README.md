### Setting up UEFI enabled macOS

**This is under development. Experiment at your own risk.**

* Install macOS by following the usual Enoch method.

* Build and use QEMU from https://github.com/kholia/qemu/. Use the "macOS"
  branch. Clover + macOS will fail to boot without this step.

* Install the included `Clover_v2*.pkg` on the main macOS disk.

  * Hit the `Customize` button during Clover install.

  * Tick 'Install for UEFI booting only', OsxAptioFix2Drv-64 and
    PartitionDxe-64 options.

* The Clover installer should leave the EFI partition mounted for us. Open that
  up in Finder.

  * Replace the `EFI/CLOVER/config.plist` file with `config.plist` included in
    this folder.

  * Put the included `q35-acpi-dsdt.aml` file into `EFI/CLOVER/ACPI/origin`
    location.

* You may edit `EFI/CLOVER/config.plist` to change the screen resolution from
  `800x600` to a higher **supported** value.

  This change also requires a corresponding change in the OVMF settings. When
  using OVMF with a virtual display (without VGA passthrough), you can set the
  client resolution in the OVMF menu, which you can reach with a press of the
  ESC button during the OVMF boot logo. In the OVMF menu settings, set Device
  Manager -> OVMF Platform Configuration -> Change Preferred Resolution for Next
  Boot to a supported value. Commit changes and exit the OVMF settings.
  Relaunch the `boot-macOS` script.

* Finally, use `boot-clover.sh` to use OVMF/UEFI to boot macOS with Clover.

* You can use `Clover Configurator` to modify your Clover configuration, if
  required.


### GPU passthrough notes

These steps will need to be adapted for your particular setup. A host machine
with IOMMU support is required. Consult the Arch Wiki article linked to at the
bottom of this file for exact requirements and other details.

I am running Ubuntu 17.04 on Intel i5-6500 + ASUS Z170-AR motherboard + NVIDIA
1050 Ti.

* Enable IOMMU support on the host machine.

  Add `iommu=pt intel_iommu=on video=efifb:off` to the `GRUB_CMDLINE_LINUX_DEFAULT` line in `/etc/default/grub` file.

* Uninstall NVIDIA drivers from the host machine and blacklist the required modules.

  ```
  $ cat /etc/modprobe.d/blacklist.conf
  ... <existing stuff>

  blacklist radeon
  blacklist nouveau
  blacklist nvidia
  ```

* Enable the required kernel modules.

  ```
  # echo "vfio" >> /etc/modules
  # echo "vfio_iommu_type1" >> /etc/modules
  # echo "vfio_pci" >> /etc/modules
  # echo "vfio_virqfd" >> /etc/modules
  ```

* Isolate the passthrough PCIe devices with vfio-pci, with the help of `lspci
  -nnk` command. Adapt these commands to suit your hardware setup.

  ```
  $ lspci -nn
  ...
  01:00.0 ... NVIDIA Corporation [GeForce GTX 1050 Ti] [10de:1c82]
  01:00.1 Audio device: NVIDIA Corporation Device [10de:0fb9]
  03:00.0 USB controller: ASMedia ASM1142 USB 3.1 Host Controller [1b21:1242]
  ```

  ```
  # echo "options vfio-pci ids=10de:1c82,10de:0fb9 disable_vga=1" > /etc/modprobe.d/vfio.conf
  ```

* Update initramfs, GRUB and then reboot.

  ```
  $ sudo update-grub2
  $ sudo update-initramfs -k all -u
  ```

* Verify that the IOMMU is enabled, and vfio_pci is working as expected.
  Consult Arch Wiki again for help on this.

* On the macOS VM, install a NVIDIA Web Driver version which is appropriate for
  the macOS version. Consult http://www.macvidcards.com/drivers.html for more
  information.

  For example, macOS 10.12.5 requires version `378.05.05.15f01` whereas macOS
  10.12.6 requires version `378.05.05.25f01`.

* Boot the macOS VM using the `boot-passthrough.sh` script. At this point, the
  display connected to your passthrough PCIe device should turn on, and you
  should see the Clover boot screen. Using the keyboard, navigate to Options ->
  Graphics Injectord, and enable `Use NVIDIA Web Driver`, then boot macOS.

* Updating SMBIOS for the macOS to `iMac14,2` might be required. I did not do
  so myself.

* To reuse the keyboard and mouse devices from the host, setup "Automatic
  login" in System Preferences in macOS and configure Synergy software.

Note: Many AMD GPU devices (e.g. AMD RX 480 & RX 580) should be natively
supported in macOS High Sierra.

Note: AMD GPU devices may require configuring Clover with `Graphics > RadeonDeInit`
key enabled.

### USB passthrough notes

These steps will need to be adapted for your particular setup.

* Isolate the passthrough PCIe devices with vfio-pci, with the help of `lspci
  -nnk` command.

  ```
  $ lspci -nn
  ...
  01:00.0 ... NVIDIA Corporation [GeForce GTX 1050 Ti] [10de:1c82]
  01:00.1 Audio device: NVIDIA Corporation Device [10de:0fb9]
  03:00.0 USB controller: ASMedia ASM1142 USB 3.1 Host Controller [1b21:1242]
  ```

  Add `1b21:1242` to `/etc/modprobe.d/vfio.conf` file in the required format.

* Update initramfs, and then reboot.

  ```
  $ sudo update-initramfs -k all -u
  ```

* Use the helper scripts to isolate the USB controller.

  ```
  $ scripts/lsgroup.sh
  ### Group 7 ###
      00:1c.0 PCI bridge: Intel Corporation Sunrise ...
  ### Group 15 ###
      06:00.0 Audio device: Creative Labs Sound Core3D ...
  ### Group 5 ###
      00:17.0 SATA controller: Intel Corporation Sunrise ...
  ### Group 13 ###
      03:00.0 USB controller: ASMedia ASM1142 USB 3.1 Host Controller
  ```

  ```
  $ scripts/vfio-group.sh 13
  ```

* Add `-device vfio-pci,host=03:00.0,bus=pcie.0 \` line to the
  `boot-passthrough.sh` script.

* Boot the VM, and devices attached to the ASMedia USB controller should just
  work under macOS.

### Synergy Notes

* Get Synergy from https://sourceforge.net/projects/synergy-stable-builds.

  I installed "synergy-v1.8.8-stable-MacOSX-x86_64.dmg" on the macOS guest and
  configured it as a client.

  For automatically starting Synergy on macOS, add Synergy to "Login Items",
  System Preferences -> Users & Groups -> Select your user account -> Login Items
  -> Add a login item

* On the Linux host machine, install "synergy-v1.8.8-stable-Linux-x86_64.deb"
  or newer, configure `~/.synergy.conf` and run `synergys` command.

* The included `.synergy.conf` will need to be adapted according to your setup.

#### Credits

* Nicholas Sherlock and others - UEFI, Clover, and other hacks

* Kyle Dayton - UEFI, Clover, and GPU passthrough notes

#### References

* https://pve.proxmox.com/wiki/Qemu/KVM_Virtual_Machines

* https://wiki.archlinux.org/index.php/PCI_passthrough_via_OVMF

* https://clover-wiki.zetam.org/configuration/smbios

* https://sourceforge.net/projects/synergy-stable-builds.

* https://wiki.archlinux.org/index.php/synergy
