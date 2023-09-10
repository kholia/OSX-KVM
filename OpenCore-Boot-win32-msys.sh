#!/usr/bin/env bash

# Special thanks to:
# https://github.com/Leoyzen/KVM-Opencore
# https://github.com/thenickdude/KVM-Opencore/
# https://github.com/qemu/qemu/blob/master/docs/usb2.txt
#
# qemu-img create -f qcow2 mac_hdd_ng.img 128G
#
# echo 1 > /sys/module/kvm/parameters/ignore_msrs (this is required)

############################################################################
# NOTE: Tweak the "MY_OPTIONS" line in case you are having booting problems!
############################################################################

MY_OPTIONS="+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check" # +pcid,+pclmulqdq,+pdpe1gb,

#1. make combined OVMF image:
# cat OVMF_VARS.fd OVMF_CODE.fd > OVMF_combined.fd
#2. whpx generates incorrect cpu info (see `lscpu -a -e` in Linux). Overcome with sockets=4,cores=1.
#3. If nothing works, use -smp 1 + `whpx,kernel-irqchip=off`
#3. Ventura: error on boot: AppleImage4: failed to sync nvram; probable resource shortage.

# This script tested with:
# MS Windows 11 22H2; QEMU 8.1; macOS 12.6.8.

ALLOCATED_RAM="8192" # MiB
CPU_SOCKETS="8" # 4, 6, 7, 8
CPU_CORES="1"
CPU_THREADS="8"

REPO_PATH="."
OVMF_DIR="."

if [ ! -f "$REPO_PATH/$OVMF_DIR/OVMF_combined.fd" ] ; then
 cat "$REPO_PATH/$OVMF_DIR/OVMF_VARS-1920x1080.fd" "$REPO_PATH/$OVMF_DIR/OVMF_CODE.fd" > "$REPO_PATH/$OVMF_DIR/OVMF_combined.fd"
fi

if [ -z `which qemu-system-x86_64` ] && [ -x "/c/Program Files/qemu/qemu-system-x86_64" ] ; then
  PATH="/c/Program Files/qemu:$PATH"
fi

# shellcheck disable=SC2054
args=(
  -m "$ALLOCATED_RAM" -cpu Westmere,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,"$MY_OPTIONS" # Penryn Nehalem Westmere  ### +svm,+rdtscp,+hypervisor,kvm=on,
  -machine q35,accel=whpx,kernel-irqchip=on
  -usb -device usb-kbd -device usb-tablet
  -smp "$CPU_THREADS",cores="$CPU_CORES",sockets="$CPU_SOCKETS"
  -device usb-ehci,id=ehci
  -device nec-usb-xhci,id=xhci
  -global nec-usb-xhci.msi=off
  -global ICH9-LPC.acpi-pci-hotplug-with-bridge-support=off
   -device usb-host,vendorid=0x8086,productid=0x0808  # 2 USD USB Sound Card
   -device usb-host,vendorid=0x1b3f,productid=0x2008  # Another 2 USD USB Sound Card
  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc"
#  -drive if=pflash,format=raw,readonly=on,file="$REPO_PATH/$OVMF_DIR/OVMF_CODE.fd"
#  -drive if=pflash,format=raw,file="$REPO_PATH/$OVMF_DIR/OVMF_VARS-1920x1080.fd"
  -bios "$REPO_PATH/$OVMF_DIR/OVMF_combined.fd"
  -smbios type=2
  -device ich9-intel-hda -device hda-duplex
  -device ich9-ahci,id=sata
  -drive id=OpenCoreBoot,if=none,snapshot=on,format=qcow2,file="$REPO_PATH/OpenCore/OpenCore.qcow2"
  -device ide-hd,bus=sata.2,drive=OpenCoreBoot
  -device ide-hd,bus=sata.3,drive=InstallMedia
  -drive id=InstallMedia,if=none,file="$REPO_PATH/BaseSystem.img",format=raw
  -drive id=MacHDD,if=none,file="$REPO_PATH/mac_hdd_ng.img",format=qcow2
  -device ide-hd,bus=sata.4,drive=MacHDD
  -netdev user,id=net0,hostfwd=tcp::10022-:22,hostfwd=tcp::18080-:8080 -device virtio-net-pci,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  -monitor stdio
  -device vmware-svga
)

#echo qemu-system-x86_64 "${args[@]}"
qemu-system-x86_64 "${args[@]}"
