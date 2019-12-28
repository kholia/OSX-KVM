#!/usr/bin/env bash

if [[ $(< /sys/module/kvm/parameters/ignore_msrs) != Y ]]; then
  echo 1 | sudo tee /sys/module/kvm/parameters/ignore_msrs
fi

############################################################################
# NOTE: Tweak the "MY_OPTIONS" line in case you are having booting problems!
############################################################################

# This works for High Sierra as well as Mojave. Tested with macOS 10.13.6 and macOS 10.14.4.

#MY_OPTIONS="+pcid,+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check"
# pcid is not supported on my machine
MY_OPTIONS="+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check"

# shellcheck disable=SC2054,SC2191,SC2034
args=(
  -enable-kvm
  -m 3072
  # Error: State blocked by non-migratable CPU device (invtsc flag)
  #-cpu "Penryn,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,$MY_OPTIONS"
  -cpu "Penryn,kvm=on,vendor=GenuineIntel,vmware-cpuid-freq=on,$MY_OPTIONS"
  -machine q35
  -smp "4,cores=2"
  -usb -device usb-kbd -device usb-tablet
  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc"
  # Error: Device 'pflash1' is writable but does not support snapshots
  #-drive "if=pflash,format=raw,readonly,file=$OVMF/OVMF_CODE.fd"
  #-drive "if=pflash,format=raw,file=$OVMF/OVMF_VARS-1024x768.fd"
  # qemu-img convert -p -f raw OVMF_CODE.fd -O qcow2 OVMF_CODE.qcow2
  # qemu-img convert -p -f raw OVMF_VARS-1024x768.fd -O qcow2 OVMF_VARS-1024x768.qcow2
  -drive if=pflash,format=qcow2,readonly,file=OVMF_CODE.qcow2
  -drive if=pflash,format=qcow2,file=OVMF_VARS-1024x768.qcow2
  -smbios type=2
  -device ich9-intel-hda -device hda-duplex
  -device ich9-ahci,id=sata
  # (qemu) qemu-system-x86_64: Device 'Clover' does not have the requested snapshot 'prepare'
  -drive id=Clover,if=none,format=qcow2,file=CloverNG.qcow2
  -device ide-hd,bus=sata.2,drive=Clover
  -drive id=MacHDD,if=none,format=qcow2,file=mac_hdd_ng.img
  -device ide-hd,bus=sata.4,drive=MacHDD
  #-netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  # during the installation, a "recovery server" is being contacted
  -netdev user,id=net0 -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:28
  -monitor stdio
  -vga vmware
  -vnc 0.0.0.0:1 -k en-us
  #-loadvm prepare
)
