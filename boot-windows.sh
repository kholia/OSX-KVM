#!/usr/bin/env bash

# Special thanks to:
# https://github.com/Leoyzen/KVM-Opencore
# https://github.com/thenickdude/KVM-Opencore/
# https://github.com/qemu/qemu/blob/master/docs/usb2.txt
#
# qemu-img create -f qcow2 windows_hdd.img 512G
#
# echo 1 > /sys/module/kvm/parameters/ignore_msrs (this is required)
#
# wget https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.208-1/virtio-win-0.1.208.iso
#
# https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md
# https://www.spice-space.org/download/windows/qxl-wddm-dod/qxl-wddm-dod-0.21/
#
# Pass the SSD (USB disk) to the VM:
# (qemu) device_add usb-host,vendorid=0x174c,productid=0x55aa

############################################################################
# NOTE: Tweak the "MY_OPTIONS" line in case you are having booting problems!
############################################################################

MY_OPTIONS="+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check"

# This script works for Big Sur, Catalina, Mojave, and High Sierra. Tested with
# macOS 10.15.6, macOS 10.14.6, and macOS 10.13.6

ALLOCATED_RAM="8192" # MiB
CPU_SOCKETS="1"
CPU_CORES="16"
CPU_THREADS="16"

REPO_PATH="."
OVMF_DIR="."

# This causes high cpu usage on the *host* side
# qemu-system-x86_64 -enable-kvm -m 3072 -cpu Penryn,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,hypervisor=off,vmx=on,kvm=off,$MY_OPTIONS\

# shellcheck disable=SC2054
args=(
  -enable-kvm -m "$ALLOCATED_RAM" -cpu host,kvm=on,+invtsc,vmware-cpuid-freq=on,"$MY_OPTIONS"
  -machine q35
  -smp "$CPU_THREADS",cores="$CPU_CORES",sockets="$CPU_SOCKETS"
  -device qemu-xhci
  -device usb-kbd
  -device usb-tablet
  -device ich9-intel-hda -device hda-duplex
  -boot d
  -drive if=pflash,format=raw,readonly=on,file="$REPO_PATH/$OVMF_DIR/OVMF_CODE.fd"
  -drive if=pflash,format=raw,file="$REPO_PATH/$OVMF_DIR/OVMF_VARS-1024x768.fd"
  -drive file="$REPO_PATH/windows.iso",media=cdrom  # Win10_21H2_English_x64.iso from Microsoft works great
  -drive file="$REPO_PATH/virtio-win-0.1.208.iso",media=cdrom
  -drive if=virtio,index=0,file="$REPO_PATH/windows_hdd.img",format=qcow2
  # -netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device e1000e,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  -netdev user,id=net0 -device e1000e,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  -monitor stdio
  -vga qxl
  # https://www.kraxel.org/blog/2021/05/qemu-cut-paste/
  # https://wiki.gentoo.org/wiki/QEMU/Windows_guest
)

qemu-system-x86_64 "${args[@]}"
