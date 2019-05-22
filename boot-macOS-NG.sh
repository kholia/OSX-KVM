#!/bin/bash

# qemu-img create -f qcow2 mac_hdd_ng.img 128G
#
# echo 1 > /sys/module/kvm/parameters/ignore_msrs (this is required)

############################################################################
# NOTE: Tweak the "MY_OPTIONS" line in case you are having booting problems!
############################################################################

# This works for High Sierra as well as Mojave. Tested with macOS 10.13.6 and macOS 10.14.4.

sudo ip tuntap add dev tap0 mode tap
sudo ip link set tap0 up promisc on
sudo brctl addif virbr0 tap0

MY_OPTIONS="+pcid,+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check"

OVMF="./"

sudo qemu-system-x86_64 -enable-kvm -m 4096 -cpu Penryn,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,$MY_OPTIONS\
	  -machine q35 \
	  -smp 4,cores=2 \
	  -usb -device usb-kbd -device usb-tablet \
	  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc" \
	  -drive if=pflash,format=raw,readonly,file=$OVMF/OVMF_CODE.fd \
	  -drive if=pflash,format=raw,file=$OVMF/OVMF_VARS-1920x1080.fd \
	  -smbios type=2 \
	  -device ich9-intel-hda -device hda-duplex \
	  -device ich9-ahci,id=sata \
	  -drive id=Clover,if=none,snapshot=on,format=qcow2,file=./'CloverNG-1920x1080.qcow2' \
	  -device ide-hd,bus=sata.2,drive=Clover \
	  -drive id=MacHDD,if=none,format=qcow2,file=./macos.qcow2 \
	  -device ide-hd,bus=sata.4,drive=MacHDD \
	  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27 \
	  -monitor stdio
