# Importing macOS into Virtual Machine Manager

Import an **already installed, shut down** macOS VM into Virtual
Machine Manager using the migration helper. It copies and verifies the installed
disk, OpenCore, firmware and existing UEFI variables, then registers the VM with
local system libvirt. It does not attach the installer or delete your originals.

```bash
# Debian/Ubuntu; install equivalents on other distributions.
sudo apt-get install python3-libvirt qemu-utils

./migrate-to-libvirt.py --dry-run
./migrate-to-libvirt.py
```

The default active directory pools are `default` (usually
`/var/lib/libvirt/images`) and `nvram` (usually
`/var/lib/libvirt/qemu/nvram`). If the latter is absent, use
`--nvram-pool default`, or select another existing directory pool. The helper
uses your authorized `qemu:///system` connection; it does not require running
the entire script as root or grant access to your home directory.

Open Virtual Machine Manager's **QEMU/KVM system connection**, select `macOS`,
and start it. Use `--start` to start after import, or `--yes` to skip the copy
confirmation. `--dry-run` performs read-only checks and prints the proposed XML.
`--help` lists source paths, pool, RAM, CPU topology and SSH port overrides.
For example:

```bash
./migrate-to-libvirt.py --name macOS-work --disk /path/to/mac.qcow2 \
    --ram 8192 --cores 4 --ssh-port 2223 --nvram-pool default
```

Keep the source VM stopped throughout copying and verification. The helper
requires self-contained QCOW2 disk/OpenCore images and raw firmware files.
Backing chains, external data files, encrypted/corrupt images, and existing
destination names are rejected. Copies need free space for the source files' full apparent sizes. Defaults match
`OpenCore-Boot.sh`; customized boot scripts are not read or executed.

The generated VM uses root-bus USB XHCI, a USB keyboard and absolute tablet,
VMware SVGA, and localhost-only SPICE with client mouse mode. Keeping USB on
the root bus avoids the input failure observed with a PCIe bridge. SPICE audio
is configured, but guest audio support depends on macOS. QEMU user networking
retains outbound connectivity and SSH forwarding on `localhost:2222`.

RAM and vCPU topology can be edited in the UI. CPU compatibility flags and the
network are custom QEMU arguments: CPU model changes must also update that
override, and the NIC will not appear as a standard editable UI network device.
The default Skylake profile follows the current script; older installations
may need `--cpu-model Haswell-noTSX` or `--cpu-model Penryn`.

Import records and normalized XML are saved under
`~/.local/share/osx-kvm-imports/<name>/`. Failed imports remove only newly
created volumes before registration; diagnostic records remain. If registration
is attempted but its response fails, imported files are retained because the VM
may already exist. Inspect libvirt before retrying. Post-registration failures
also retain the VM and its files. No host-boot autostart is
enabled. The original `OpenCore-Boot.sh` still boots the original disk copy,
which can diverge from the imported VM. Source cleanup is deliberately manual.

## Manual XML alternative


- Edit `macOS-libvirt-Catalina.xml` file and change the various file paths (search
  for `CHANGEME` strings in that file). The following command should do the
  trick usually.

  ```
  sed "s/CHANGEME/$USER/g" macOS-libvirt-Catalina.xml > macOS.xml

  virt-xml-validate macOS.xml
  ```

- Create a VM by running the following command.

  ```bash
  virsh --connect qemu:///system define macOS.xml
  ```

- If needed, grant necessary permissions to libvirt-qemu user,

  ```
  sudo setfacl -m u:libvirt-qemu:rx /home/$USER
  sudo setfacl -R -m u:libvirt-qemu:rx /home/$USER/OSX-KVM
  ```

- Launch `virt-manager` and start the `macOS` virtual machine.

## Testing the helper

```bash
python3 -m unittest discover -s tests -v
OSX_KVM_LIBVIRT_TESTS=1 /usr/bin/python3 -m unittest discover -s tests -v
```

The opt-in integration tests require access to local system libvirt. They use
small temporary images, separately named transient storage pools and inactive
test domains, and remove their own fixtures. They never start a guest or change
an existing VM. They do not replace guest boot and interactive console checks.
